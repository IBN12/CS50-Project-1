from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from markdown2 import Markdown
from random import randint, randrange

from . import util

# class - NewSearchForm()
class NewSearchForm(forms.Form):
    searchEntry = forms.CharField(label="Enter Here")
    
# class - CreateNewPageForm()
class CreateNewPageForm(forms.Form):
    pageName = forms.CharField(max_length=100, label="") # Text box where the user will enter a new page name.
    pageContent = forms.CharField(label="" ,widget=forms.Textarea) # Text area where the users will enter content for the new page.

    pageName.widget.attrs.update({'class': 'New_Page_Text_Box', 'placeholder': 'Enter New Page Name'}) 
    pageContent.widget.attrs.update({'class': 'Content_Text_Area', 'rows':15, 'cols': 80, 'placeholder': 'Enter Content'})

# class object - markdowner
markdowner = Markdown() 

# Function Definition - index
# Precondition: The index page will be main page with a
#               sidebar and main section.
def index(request):
    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = NewSearchForm(request.POST)
        # Check if form data is valid (server-side)
        if form.is_valid():
            # Isolate the message from the 'cleaned' version of form data
            searchEntry = form.cleaned_data["searchEntry"]

            # Check if the search entry that the 
            # user entered into the form is correct.
            for entry in util.list_entries():
                if entry == searchEntry:
                    content = util.get_entry(entry)
                    correctEntry = True
                    break
                else:
                    content = None
                    correctEntry = False

            # Check if content is None
            if content != None:
                # Converts markdown to HTML code
                htmlContent = markdowner.convert(content)
            else:
                entryListResult = []
                myEntry = str(searchEntry)

                # Algorithm will take the user to a result page
                # that has a similar entry to the user query entry.
                # Note: Will keep trying to improve this algorithm
                #       because there will be new entries added to
                #       the encyclopedia. 
                for entry in util.list_entries():
                    entryIndex = 0
                    match = 0
                    noMatch = 0

                    # Part 1: Convert the letters in myEntry to lowercase if they aren't already.
                    myEntryLowerCase = myEntry.lower()

                    # Part 2: Eliminate white spaces in the entry string if the there any.
                    entryNoWhiteSpace = str(entry).replace(" ", "")

                    # Part 3: Convert the letters in the entry to lower case.
                    # Assign the letters from the entry to a list.s
                    entryLetterList = []
                    for letters in entryNoWhiteSpace:
                        entryLetterList.append(letters.lower())
                    
                    # Part 4: Sort the list
                    entryLetterList.sort()

                    # Part 5: Find the length of the entryList
                    entryLetterListLength = len(entryLetterList)

                    # Part 6: Find letters from each of the entries that match the search entry (myEntry)
                    for num in range(entryIndex, entryLetterListLength):
                        # Part 6 (a): Find the identical letters to eliminate them from the match up sequence
                        identicalLetters = entryLetterList.count(entryLetterList[num])
                        identicalLetters -= 1

                        # Part 6 (b): Take the identical letters out and find letters that match the search entry
                        if identicalLetters >= 1:
                            while identicalLetters > 0:
                                identicalLetters -= 1
                                # noMatch += 1
                                entryIndex += 1
                            found = myEntryLowerCase.find(entryLetterList[num])
                            entryIndex += 1
                        elif identicalLetters == 0:
                            found = myEntryLowerCase.find(entryLetterList[num])
                            entryIndex += 1
                        
                        # Part 6 (c): Increment match or noMatch based on the find function results
                        if found >= 0:
                            match += 1
                        elif found == -1:
                            noMatch += 1

                    # Part 7: Conclusion - append entries that match
                    if match > noMatch:
                        entryListResult.append(entry)
                        entryLetterList.clear() # Clear the letter list for use again.

            # Check if the entry is correct
            if correctEntry:
                return render(request, "encyclopedia/search.html", {
                    "htmlContent": htmlContent, "TITLE": searchEntry, "correctEntry": correctEntry
                })
            else:
                return render(request, "encyclopedia/search.html", {
                    "TITLE": searchEntry, "correctEntry": correctEntry, "entryListResult": entryListResult
                })
        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/index.html", {
                "form": form, "entries": util.list_entries()
            })
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": NewSearchForm
    })


# Function Definition - search
# Precondition: Will allow the user to search for the
#                 entires in the list_entries() function
#                 by URL. 
def search(request, TITLE):
    # Search for the correct entry.
    for entry in util.list_entries():
        if TITLE == entry:
            content = util.get_entry(TITLE)
            correctEntry = True
            break
        else:
            content = None
            correctEntry = False
    
    # Check if the content is None
    if content != None:
        # Convert markdown to html code. 
        htmlContent= markdowner.convert(content) 
    else:
        # Give message when there is no content provided.
        htmlContent = "No content is provided."
    
    # Check if the entry is correct
    if correctEntry:
        return render(request, "encyclopedia/search.html", {
            "TITLE": TITLE, "correctEntry": correctEntry, "htmlContent": htmlContent
        })
    else:
        return render(request, "encyclopedia/search.html", {
            "TITLE": TITLE, "correctEntry": correctEntry, "htmlContent": htmlContent
        })


# Function Definition - new_page
# Precondition: Will allow the user to create a new page
#               and enter Markdown for the page.
def new_page(request):
    # Check if the method is a Post
    if request.method == "POST":
        # Take in the data the user submitted and save it as newPageForm
        newPageForm = CreateNewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if newPageForm.is_valid():
            # Isolate the pageName and pageContent from
            # the 'cleaned' version of newPageFrom data
            pageName = newPageForm.cleaned_data["pageName"]
            pageContent = newPageForm.cleaned_data["pageContent"]

            # Find out if the page already exist. If the page
            # does exist then an error message will be provided.
            # If the page does not exist then the user will be taken
            # back to the index page to view the new entry.
            pageExist = util.get_entry(pageName)
            if pageExist == None: # Page does not exist.
                # Save the new pageName and pageContent to the encyclopedia.
                util.save_entry(pageName, pageContent)
                return HttpResponseRedirect(reverse("encyclopedia:index"))
            else: # Page does exist.
                pageMessage = "This encyclopedia entry already exist."
                pageAlreadyExist = True
                return render (request, "encyclopedia/new_page.html", {
                    "pageMessage": pageMessage, "pageAlreadyExist": pageAlreadyExist
                })
        else:
            # if the form is invalid, re-render the page with existing infromation.
            return render(request, "encyclopedia/new_page.html",{
                "newPageForm": newPageForm
            })
    return render(request, "encyclopedia/new_page.html", {
        "newPageForm": CreateNewPageForm
    })


# Function Definition - edit_page
# precondition: Will allow the user to edit an encyclopedia entry
def edit_page(request, TITLE):
    # Grab the original content that thats will pre-populate the textarea
    originalContent = util.get_entry(TITLE)

    # Check if method is POST
    if request.method == "POST":
        # Isolate the data from the POST that was sent to server and assign it to editContent.
        editContent = request.POST["editContent"]

        # Save editContent to an original encyclopedia title.
        util.save_entry(TITLE, editContent)

        # Bring the user back to the index page.
        return HttpResponseRedirect(reverse("encyclopedia:index"))
    return render(request, "encyclopedia/edit_page.html",{
        "originalContent": originalContent, "TITLE": TITLE
    })


# Function Definition - Random
# Precondition: Will take the user to a random entry page in the encyclopedia.
def random(request):
    entryList = []
    # send the entries to a new list
    for entry in util.list_entries():
        entryList.append(entry)
    
    # gather the length and a random number
    length = len(entryList)
    randomNum = randrange(0, length)

    # assign a random entry
    randomEntry = entryList[randomNum]
    return render(request, "encyclopedia/random.html", {
        "randomEntry": randomEntry
    })