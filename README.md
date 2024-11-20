# visa-checker
A program for regularly checking available places for a visa

Instructions for Setup
Install Dependencies:
<ul> 
<li> Ensure you have Python, pip, and MySQL installed. </li>
Install required Python packages:
  <b>pip install python-dotenv telebot mysql-connector-python selenium
<b/></li> <ul/>

<ol>
<li> Set Up Database:
Run the SQL commands from database.sql to create the required database and tables in MySQL. </li>
<li> Configure Environment Variables:
Create a .env file in the project directory with the content provided in the .env section, replacing placeholder values with actual credentials. </li>
<li>Setup ChromeDriver: 
Download ChromeDriver and place it in an appropriate directory. Update the path in the start_driver() function if necessary. </li>
<li> Run the Bot:
python telegram.py </li>


</ol>
<h4> Notes </h4>
  <ul> 
  <li>
    Ensure the MySQL server is running and accessible.  </li>
<li>Adjust the SCHEDULE_URL and APPOINTMENTS_URL as needed based on your specific use case. </li>
<li>Be cautious with credentials;
    do not expose .env files publicly. </li>

    <li> The parsing code collects dates only for Almaty and Astana (to change the city to Almaty, remove the setter) I advise you to change the link to track the city that suits you.</li>
    <li> Also there is only Russian interface , in future i am planning to add more languages support </li> 
 </ul>
<img src = "https://github.com/user-attachments/assets/ca0683b6-ab59-4595-847f-aea489aba9b8" >

