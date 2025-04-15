from flask import url_for
from flask_wtf import FlaskForm
import mongoengine.errors
from wtforms.validators import URL, Email, DataRequired, NumberRange
from wtforms.validators import URL, Email, DataRequired
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, FileField, BooleanField, URLField
from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Blog, Comment, Internship
from app.classes.forms import BlogForm, CommentForm, InternshipForm
from flask_login import login_required
import datetime as dt
from bson.objectid import ObjectId


@app.route('/internship/new', methods=['GET', 'POST'])
@login_required
def internshipNew():
    # Create the form object from the InternshipForm
    form = InternshipForm()

    # Check if the form is valid and submitted
    if form.validate_on_submit():
        # Create a new Internship object from the form data
        newInternship = Internship(
            subject=form.subject.data,
            content=form.content.data,
            tag=form.tag.data,
            author=current_user.id,
            create_date=dt.datetime.utcnow,  # Set create_date to current UTC time
            modify_date=dt.datetime.utcnow  # Set modify_date to the same time
        )

        # Save the new internship object to the MongoDB database
        newInternship.save()

        # Redirect to the 'internship' route and pass the internshipID
        return redirect(url_for('internship', internshipID=newInternship.id))

    # If the form is not submitted or invalid, render the form page again
    return render_template('internshipform.html', form=form)


@app.route('/internship/<internshipID>')
def internship(internshipID):
    internship = Internship.objects.get(id=internshipID)  # Fetch the internship by ID
    return render_template('internship.html', internship=internship)

@app.route('/internship/list')
def internshipList():
    internships = Internship.objects()  # Fetch all internship entries
    return render_template('internships.html', internships=internships)

@app.route('/internship/edit/<internshipID>', methods=['GET', 'POST'])
@login_required
def internshipEdit(internshipID):
    internship = Internship.objects.get(id=internshipID)

    # Ensure only the author can edit
    if internship.author != current_user.id:
        flash("You are not authorized to edit this internship.")
        return redirect(url_for('internship', internshipID=internship.id))

    form = InternshipForm(obj=internship)

    if form.validate_on_submit():
        internship.subject = form.subject.data
        internship.content = form.content.data
        internship.tag = form.tag.data
        internship.modify_date = dt.datetime.utcnow()
        internship.save()
        return redirect(url_for('internship', internshipID=internship.id))

    return render_template('internshipform.html', form=form)

@app.route('/internship/delete/<internshipID>')
@login_required
def internshipDelete(internshipID):
    internship = Internship.objects.get(id=internshipID)

    # Only the author can delete
    if str(internship.author.id) != str(current_user.id):
        flash("You are not authorized to delete this internship.")
        return redirect(url_for('internship', internshipID=internship.id))

    internship.delete()
    flash("Internship deleted.")
    return redirect(url_for('internshipList'))  
