
a. **Title and Deployment URL**
   - Title: MyGarden App
   - Deployment URL: [https://www.mygardenapp.com](https://www.mygardenapp.com)

b. **Description**
   The Romaine Calm is a web application that allows users to manage their gardens online. Users can create and track multiple gardens, add plants to each garden. They can keep track of what plants they have, and save plants that they might want to have in the future

c. **Implemented Features and Rationale**
   - User Registration and Authentication: Implemented user registration and authentication to allow users to create accounts and securely log in. This feature ensures that each user can manage their own set of gardens and associated data.
   - Garden Creation: Users can create multiple gardens with unique names. This allows users to organize and manage different garden projects or locations.
   - Plant Management: Users can add plants to their gardens, providing information such as images, plant name and species. This feature enables users to keep track of the plants they have in each garden.
   - API Integration: The application integrates with a plant API to search for information on a variety of plants.
   - 
d. **Standard User Flow**
   1. User visits the Romaine Calm homepage and clicks on the "Sign Up" button.
   2. User fills in the registration form, providing a unique username, email address, and password.
   3. User submits the registration form and is directed to the search for plants page.
   4. User can search for plants by name, this returns a list of plants connected to that specific name
   5. User can select a specific plant to retrieve more information. 
   6. User has the option to save a plant and is redirected to the garden page
   7. User can save the garden to the predefined gardens "My Garden" or "Future Garden"
   8. User creates a new garden by entering a unique name and clicking on the "Create Garden" button.
   9.  User can update or delete gardens, or plants.

e. **API Integration**
   - The Romaine Calm integrates with a plant API (http://trefle.io/api/v1) to provide users with a robust information about plants.
   - The API provides a comprehensive database of plant species.
   - Users can access the API through the app's interface, allowing them to search for specific plants, and learn about their characteristics.

f. **Technology Stack**
   - Front-end: HTML, CSS, JavaScript
   - Back-end: Python 7.0.1, Flask-SQLAlchemy 2.3.2 
   - Database: PostgreSQL
   - API Integration: RESTful API

g. **Additional Notes**
   - The MyGarden App aims to provide a user-friendly and intuitive interface for garden enthusiasts to manage their gardens effectively.
   - The app focuses on simplicity, allowing users to quickly create gardens, and add plants.
  