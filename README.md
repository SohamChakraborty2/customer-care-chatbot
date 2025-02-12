🗣️ Customer Care Chatbot
An AI-powered customer care chatbot built with Rasa for handling user queries efficiently. It can assist with common customer support tasks like FAQs, ticket management, and account-related issues, providing an interactive and automated experience.

🚀 Features
✅ Intent Recognition – Understands user queries and responds accordingly
✅ Slot Filling & Forms – Collects necessary user information before proceeding
✅ Custom Actions – Executes backend logic (e.g., fetching order status, raising support tickets)
✅ Interactive Conversations – Supports multi-turn dialogues for better user experience
✅ API Integration – Connects with external services for real-time data
✅ Scalable & Extensible – Easily customizable to add new functionalities

🛠️ Tech Stack
Backend: Rasa (NLP & Dialogue Management)
Frontend: Rasa X (Optional UI for testing)
Database: SQLite / PostgreSQL (Optional for storing user interactions)
APIs: Integrated for fetching user details and support ticket creation
🔧 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/SohamChakraborty2/customer-care-chatbot.git
cd customer-care-chatbot



2️⃣ Create a Virtual Environment & Install Dependencies

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt




3️⃣ Train the Model

rasa train




4️⃣ Run the Chatbot

rasa run --enable-api



5️⃣ Start the Interactive Chat Interface

rasa shell



🏗️ Folder Structure

📂 customer-care-chatbot  
│── 📂 actions/            # Custom action files  
│── 📂 data/               # Training data (nlu.yml, rules.yml, stories.yml)  
│── 📂 models/             # Trained models  
│── 📂 domain.yml          # Defines intents, entities, and responses  
│── 📂 config.yml          # Model pipeline and policies  
│── 📂 credentials.yml     # API credentials  
│── 📂 endpoints.yml       # Server endpoints for custom actions  
│── 📂 README.md           # Project documentation  


📌 Example Queries
User: "I want to check my account balance."
Bot: "Sure! Can you provide your registered phone number?"

User: "How can I raise a support ticket?"
Bot: "I can help with that. Please describe your issue."

🤝 Contributing
Feel free to fork this repo and submit pull requests! If you have any suggestions or issues, open a ticket in the Issues section.

📜 License
This project is licensed under the MIT License. See LICENSE for details.

📬 Contact
📧 Soham Chakraborty
🌐 LinkedIn | GitHub
