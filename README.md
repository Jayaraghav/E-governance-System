# E-Governance System

Welcome to the E-Governance System repository! This project aims to digitize and streamline government services, making them more accessible, transparent, and efficient for both citizens and government employees. It uses a combination of Python (Flask), MySQL, and front-end technologies to deliver an intuitive web platform for managing various government services.

## Project Overview

The E-Governance System offers role-based dashboards, allowing employees to manage government services, departments, and Common Service Centers (CSCs), while citizens can easily access essential services, job vacancies, PDS details, and government project information.

### **Key Features:**
- **Employee Dashboard:** Tools for managing services, CSCs, and data with secure login and access control.
- **Citizen Dashboard:** Access to government services, job vacancies, and updates on government projects.
- **Role-based Access:** Secure login and permissions ensure everyone gets the right level of access.

## Repository Structure

- **`E-governance_Flas_Connectivity.py`**: The main Python file that runs the Flask web application, handling the backend logic and connecting to the database.
- **`templates/`**: Contains HTML, CSS, and JavaScript files that form the frontend of the E-Governance web platform. The templates include:
  - **`Citizen Dashboard`**: A dashboard for citizens to view and interact with services.
  - **`Employee Dashboard`**: A dashboard for employees to manage services and data.
  - **`Login`**: The login page for secure authentication.
  - **`Vacancies`**: A page displaying job vacancies available through government programs.
  - **`Services Index`**: A page listing all government services available to citizens.
  - Other HTML, CSS, and JavaScript files: These handle various elements of the user interface, ensuring the web platform is responsive and user-friendly.
  
- **`SQL_commands/`**: SQL files for creating the database, inserting data, and managing the system’s backend.
  - **Create and Insert Commands**: SQL scripts to set up the database and populate it with initial data.
- **`Project_Description.pdf`**: A detailed PDF document containing the full project description, system analysis, ER diagram, and other relevant documentation.

## How to Use

1. **Clone the Repository**:
   Clone the repository to your local machine using the following command:
   ```bash
   git clone https://github.com/Jayaraghav/E-governance-System.git
