DESIGN.md

Login -
    In order to create the log in page, I essentially took the framework from the log in page in finance. The user enters a username and a password and if it matches one of the users in users table in the database then the user is admitted into the index page or else an error message is displayed.

Index -
    For the index page, I essentially created a table with information from the parties table in the data base. The way I got the information from the datbase to the html page was through using a sql select query to get info on all the parties. All information was directly placed onto the table excpet for host name and the date. For the host field, I had to get the hostID from the parties table and then cross reference that with the userIDs. For the date, I had to change the format in order to display the information in a cleaner and more concsice way.

Make -
    For the make page, I got the information posted from the html page and then entered that information into a parties table in the database.

RSVP -
    For the RSVP page I used both the get and post methods. For the get method, I returned the rsvp.html page along with a list of all of the party names in order to be displayed in the drop down menu. For the post method, I got the name of the party the user wanted to rsvp to along with their offering and entered that information into a rsvp table.
Map -
    The map page was for certainly the most technically difficult aspect of my project. This page only has a get method in which a dictionary is created with the names of the parties as keys and the values being lists of information of the parties. Additionally, the dictionary was placed into the sessions dictionary which is a global object for reasons later explained. In terms of actually including a map in my html page there was a lot of script work to be done. I learned basic framework from online but I had to also learn how to work with APIs. Essentially, I had to get two seperate APIs to implement my map and it eventually worked. For the actual script, it begins with placing the map on a specific spot in the world. I chose to use the coordinates of the Harvard yard considering that this would be a website used here on campus.I then went onto a for loop of that iterates through the dictionary with information of all the parties in order to create markers on the map. The markers take a few values as input. First off, I used an emoji as the picture for each of my markers. Furthermore, the markers also take in a set of coordinates which were stored as values in each key. Additionally, each marker is given a number based on how many parties are located in that dorm. Finally, each marker is given a specific url. Each marker has a unique url because I used the addListener method in order to make each marker a link to a page that displays a table with all the parties being held in that location.

RSVP info -
    For the rsvp info page, I used both the post and get method. In the get method, simillar to the rsvp page, I created a drop down menu with all the names of parties. Once the submit button is clicked, the information is posted. Once posted, the user is redirected to a html page with a table with all of the rsvp information.

Change password -
    On this page, the user just posts a new password and the data base is updated through a sql command.
Logout -
    The session information is cleared.
