# Influencer Marketing Platform

A web application built with Flask designed to connect sponsors and influencers for marketing collaborations. This platform allows sponsors to create and manage campaigns, find influencers, and manage ad requests. Influencers can browse campaigns, submit requests to collaborate, and manage incoming requests from sponsors. An admin panel provides oversight and management capabilities.

## Table of Contents

-   [Project Overview](#project-overview)
-   [Features](#features)
-   [Technologies Used](#technologies-used)
-   [Database Schema](#database-schema)
-   [Setup and Installation](#setup-and-installation)
-   [Usage](#usage)
-   [Key Routes](#key-routes)
-   [Admin Functionality](#admin-functionality)
-   [Future Improvements](#future-improvements)
-   [Author](#author)

## Project Overview

The Influencer Marketing Platform aims to streamline the process of collaboration between businesses (sponsors) seeking promotion and social media personalities (influencers).

-   **Sponsors:** Can create marketing campaigns (public or private), search for relevant influencers, send specific ad requests, and manage requests submitted by influencers for their public campaigns.
-   **Influencers:** Can build their profile, search for public campaigns fitting their niche, submit ad requests to sponsors, and accept/reject requests sent directly by sponsors.
-   **Admin:** Can monitor the platform, search for users and campaigns, view details, remove problematic accounts or campaigns, and view platform statistics.

## Features

**General:**
*   User Registration (Sponsor & Influencer)
*   User Login (Sponsor, Influencer, Admin)
*   Password Hashing for Security
*   Session Management
*   User Logout

**Sponsor:**
*   Sponsor Profile Dashboard
*   Create, View, Edit, and Delete Campaigns
*   Set Campaign Visibility (Public/Private)
*   Search for Influencers
*   Create Ad Requests (Target specific influencers for private campaigns or make general for public)
*   View Ad Requests received from Influencers for public campaigns
*   Accept/Reject Ad Requests submitted by Influencers
*   View Active/Accepted Collaborations

**Influencer:**
*   Influencer Profile Dashboard
*   View Active/Accepted Collaborations
*   View Pending Ad Requests received from Sponsors
*   Accept/Reject Ad Requests from Sponsors
*   Search/Browse Public Campaigns
*   Submit Ad Requests to Sponsors for Public Campaigns

**Admin:**
*   Admin Login & Dashboard
*   Search for Sponsors, Influencers, and Campaigns
*   View details of specific users or campaigns
*   Delete (Flag/Remove) Sponsors, Influencers, or Campaigns (handles related data like ad requests)
*   View Platform Statistics (User counts, Campaign visibility breakdown) visualized with charts.

## Technologies Used

*   **Backend:** Python
*   **Web Framework:** Flask
*   **Database:** SQLite
*   **ORM:** SQLAlchemy, Flask-SQLAlchemy
*   **Database Migrations:** Flask-Migrate
*   **Password Security:** Werkzeug (PBKDF2-SHA256 Hashing)
*   **Templating:** Jinja2
*   **Plotting (Admin Stats):** Matplotlib
*   **Frontend:** HTML, CSS, JavaScript (basic interaction)

## Database Schema

The application uses a relational database with the following core models:

*   **`Admin`**: Stores admin credentials.
*   **`User`**: Base class for users, storing common info (username, hashed password, user type). Uses single-table inheritance.
*   **`Sponsor`**: Inherits from `User`, adds `industry`. Has a one-to-many relationship with `Campaign`.
*   **`Influencer`**: Inherits from `User`, adds `platform_presence`. Has a one-to-many relationship with `AdRequest`.
*   **`Campaign`**: Stores details about a marketing campaign (title, description, niche, budget, visibility, etc.). Belongs to one `Sponsor`. Has a one-to-many relationship with `AdRequest`.
*   **`AdRequest`**: Represents a collaboration request or agreement. Links a `Sponsor`, an `Influencer` (can be null initially for public campaign requests from influencers), and a `Campaign`. Stores request details (ad specifics, payment, status).

*(Refer to the ER Diagram in the project report for a visual representation of relationships).*

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.x
    *   `pip` (Python package installer)
    *   `git` (for cloning)

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/lokabhiramchintada/Influencer_Marketing_Platform
    cd Influencer_Marketing_Platform
    ```

3.  **Create and Activate a Virtual Environment (Recommended):**
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

4.  **Install Dependencies:**
    *   First, ensure you have a `requirements.txt` file. If not, create one from the imports in `app.py` or generate it if you have the environment set up:
        ```bash
        # Make sure Flask, Flask-SQLAlchemy, Flask-Migrate, Werkzeug, Matplotlib are installed
        pip freeze > requirements.txt
        ```
    *   Install from the requirements file:
        ```bash
        pip install -r requirements.txt
        ```
        *(Make sure `requirements.txt` includes Flask, Flask-SQLAlchemy, Flask-Migrate, Werkzeug, Matplotlib)*

5.  **Database Setup:**
    *   Initialize the migration environment (run only once per project):
        ```bash
        flask db init
        ```
    *   Create the initial database migration script:
        ```bash
        flask db migrate -m "Initial migration"
        ```
    *   Apply the migration to create the database schema (`myproject.db` will be created):
        ```bash
        flask db upgrade
        ```

6.  **Create Initial Admin User:**
    *   This application does not have an admin registration interface. You need to create the first admin user manually. You can do this using the Flask shell or a simple script.
    *   **Using Flask Shell:**
        ```bash
        flask shell
        ```
        Inside the shell:
        ```python
        from app import db, Admin  # Or wherever your models and db are defined
        from werkzeug.security import generate_password_hash

        # Replace 'admin_user' and 'your_secure_password' with desired credentials
        admin_username = 'admin_user'
        admin_password = 'your_secure_password'

        hashed_pw = generate_password_hash(admin_password, method='pbkdf2:sha256')
        new_admin = Admin(admin=admin_username, password=hashed_pw)
        db.session.add(new_admin)
        db.session.commit()
        exit()
        ```

7.  **Run the Application:**
    ```bash
    flask run
    ```
    The application should now be running, typically at `http://127.0.0.1:5000/`.

## Usage

1.  Access the application in your web browser (e.g., `http://127.0.0.1:5000/`).
2.  Register as either an Influencer or a Sponsor using the respective registration links/pages.
3.  Log in using your registered credentials via the User Login page.
4.  **Sponsors:** Navigate to your profile, create campaigns, search for influencers, manage ad requests.
5.  **Influencers:** Navigate to your profile, browse public campaigns, submit requests, manage incoming requests.
6.  **Admin:** Log in via the Admin Login page (`/admin/login`) using the credentials created during setup. Access the dashboard to monitor and manage the platform.

## Key Routes

*   `/`: Welcome page.
*   `/admin/login`: Admin login page.
*   `/admin/profile`: Admin dashboard.
*   `/admin/search`: (GET - AJAX endpoint) Search for users/campaigns.
*   `/admin/flag/<item_type>/<item_id>`: (POST) Delete a user or campaign.
*   `/admin/view/<item_type>/<item_id>`: (GET - AJAX endpoint) Get details of a user/campaign.
*   `/admin/stats`: View platform statistics charts.
*   `/admin_logout`: Logout admin user.
*   `/user/login`: Sponsor/Influencer login page.
*   `/user/influencer_register`: Influencer registration page.
*   `/register/influencer`: (POST) Handle influencer registration.
*   `/user/sponsor_register`: Sponsor registration page.
*   `/register/sponsor`: (POST) Handle sponsor registration.
*   `/influencer/profile`: Influencer dashboard.
*   `/influencer/find`: Influencer page to browse public campaigns.
*   `/sponsor/profile/<username>`: Sponsor dashboard.
*   `/sponsor/campaigns`: Sponsor page to manage campaigns (view, add, link to edit/delete).
*   `/sponsor/campaign/edit/<campaign_id>`: (GET/POST) Edit an existing campaign.
*   `/sponsor/campaign/delete/<campaign_id>`: (POST) Delete a campaign.
*   `/sponsor/find`: Sponsor page to search for influencers/campaigns.
*   `/search_influencers`: (GET - AJAX endpoint) Search influencers (used in ad request forms).
*   `/ad_request/create`: (POST) Sponsor creates an ad request.
*   `/submit_ad_request`: (POST) Influencer submits an ad request for a public campaign.
*   `/ad_request/<request_id>/accept`: (POST) Influencer accepts a request.
*   `/ad_request/<request_id>/reject`: (POST) Influencer rejects a request.
*   `/sponsor/ad_request/<request_id>/accept`: (POST) Sponsor accepts a request from an influencer.
*   `/sponsor/ad_request/<request_id>/reject`: (POST) Sponsor rejects a request from an influencer.
*   `/logout`: Logout sponsor/influencer user.

## Admin Functionality

The admin panel provides tools for platform oversight:

*   **Search:** Find specific sponsors, influencers, or campaigns using keywords.
*   **View Details:** Get basic information about a selected item from the search results.
*   **Delete (Flag):** Remove users or campaigns from the platform. This action also removes associated ad requests to maintain data integrity.
*   **Statistics:** Visualize key platform metrics like the number of sponsors vs. influencers and the distribution of public vs. private campaigns.

## Future Improvements

*   **Notifications:** Implement a notification system for new requests, status changes, etc.
*   **Advanced Search/Filtering:** More granular search options for campaigns (budget range, date range) and influencers (platform specifics, follower count - *would require adding these fields*).
*   **Direct Messaging:** Allow sponsors and influencers to communicate directly within the platform.
*   **Campaign Performance Tracking:** Add features for sponsors/influencers to report on campaign results (e.g., reach, engagement).
*   **Rating/Review System:** Allow sponsors and influencers to rate each other after a collaboration.
*   **Payment Integration:** Integrate with a payment gateway for handling payments securely.
*   **RESTful API Endpoints:** Expose data via dedicated `/api/` routes for potential external use or a decoupled frontend.
*   **Admin User Management:** Add UI for creating/managing admin users instead of manual creation.
*   **Unit & Integration Testing:** Add tests to ensure code reliability.

## Author

*   **Chintada Lokabhiram**
*   Roll Number: 22f1001409