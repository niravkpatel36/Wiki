# Wiki

Wiki is a Django-based web application inspired by Wikipedia. It allows users to view, search, create, edit, and randomly explore encyclopedia entries. Each entry is written in Markdown and dynamically converted to HTML when displayed, making content easy to write while remaining visually structured for readers.

## Features

### Entry Pages

- Each encyclopedia entry has its own dedicated page.
- Pages are accessed via ```/wiki/TITLE```.
- Entry content is written in Markdown and rendered as HTML.
- If a requested page does not exist, a custom error page is displayed.

### Index Page

- Displays a list of all encyclopedia entries.
- Each entry name is clickable and links directly to its page.

### Search

- Users can search for entries using the sidebar search box.
- If the query exactly matches an entry title, the user is redirected to that page.
- If there is no exact match, a search results page displays all entries containing the query as a substring.
- Search is case insensitive.

### Create New Page

- Users can create new encyclopedia entries by providing a title and Markdown content.
- If an entry with the same title already exists, an error message is shown.
- Successful creation redirects the user to the newly created entry page.

### Edit Page

- Each entry page includes an Edit link.
- The edit form is pre-populated with the existing Markdown content.
- After saving changes, users are redirected back to the entry page.

### Random Page

- The Random Page option redirects the user to a randomly selected encyclopedia entry.

### Markdown Conversion

- Markdown content is converted to HTML using the markdown2 Python package.
- Supports headings, bold text, links, lists, and paragraphs.

## Installation and Setup

### Clone the repository:
```
git clone https://github.com/niravkpatel36/Wiki.git
```

### Navigate to the project directory:
```
cd wiki
```

### Install dependencies:
```
pip3 install django markdown2
```

### Run database migrations:
```
python manage.py migrate
```

### Start the development server:
```
python manage.py runserver
```

The web application will be served at http://127.0.0.1:8000/.

## Acknowledgments

This project was completed as part of CS50 Web Programming with Python and JavaScript. Starter code and project specifications were provided by Harvard University.
