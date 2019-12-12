
# Group 16 – Frontend
Mahmoud Thabit

# Sprint 4
Goals for Sprint 4

Implement at least Three Call/Visualization and Deploy to a server

API: http://augur.osshealth.io/api_docs/

Webite: http://18.218.250.185/


# Deployment
To deploy this application, any server running apache would work however I used AWS


**Step 1**: Create an AWS instance in EC2 (Amazon Linux AMI (HVM), SSD Volume Type)

**Step 2**: select t2.micro with 1GB Memory

**Step 3**: all the default settings are good

**Step 4**: add storage, a recommended size is 8.00 GB

**Step 5**: Add Tages, no changes are needed

**Step 6**: Configuration Security Group: make sure SSH is added, you will need to add HTTP Port: 80 and HTTPS Port: 443

**Step 7**: Review everything before launching an instance.


you will need to login to the server and configure everything

after logging in you need to run some commands
-: sudo yum update -y

-: sudo yum install -y httpd24 php70 mysql56-server php70-mysqlnd

-: sudo service httpd start


now you need to change file permissions so you can upload the code

navigate to ls "/var/www" using command -: ls -l /var/www

after navigating to the directory, run this command -: sudo chmod 2775 /var/www


after that use the preferred method to upload the code to "/var/www/html/" directory.


[https://medium.com/@oreillyalan88/lamp-linux-apache-mysql-php-web-server-on-an-amazon-ec2-linux-instance-e37eb023e996](https://medium.com/@oreillyalan88/lamp-linux-apache-mysql-php-web-server-on-an-amazon-ec2-linux-instance-e37eb023e996)


# Files
- **index.html** (added): the main landing page and contains the code for Top Committer web page

- **index.css** (added): the CSS styling sheet to make the web page look good

- **issue.html** (added): the second web page which displays the Average Issue Response Time

- **summary.html** (added): the third web page which displays the Aggregate Summary per Group

- **fork.html** (added): the fourth web page which displays the number of forks a repo has

- **bar.css** (added): a CSS styling sheet to make sure that all the bar on the web page are uniform


# Dependencies
Database used for the API calls: http://augur.osshealth.io/api_docs/

CanvasJS used for graphs: https://canvasjs.com/assets/script/canvasjs.min.js


# Navigating the website
The top bar will let you navigate the different web pages

The blue buttons are linked to the different repository groups


# Top Committers by percentage:
Will use a pie chart to show the distribution of commits for groups

Purpose: to show a developer how spread out the work is, if the top committer is very dominated, then it is not as spread out.

API: Top Committers (Repo Group) (/repo-groups/:repo_group_id/top-committers)

http://augur.osshealth.io:5000/api/unstable/repo-groups/24/top-committers



# Get Average Issue Response Time:
Will get the Average Issue Resolution Time and display as a bar char

Purpose: to show a developer how long it takes for a Response time to an issue, helps developers see how active members are in each repo and as a repo group.

API: Evolution - Issue Response Time (Repo Group)( /repo-groups/:repo_group_id/issues-maintainer-response-duration)

http://augur.osshealth.io:5000/api/unstable/repo-groups/24/issues-maintainer-response-duration



# Get Aggregate Summary per Group
Will just display the information that give us a summery of what repo group is like("watcher_count", "star_count", "fork_count", "merged_count", "committer_count", and "commit_count")

Purpose: to show a developer basic information on the repo group, for quick evaluation.

API: Aggregate Summary (Repo Group) (/repo-groups/:repo_group_id/aggregate-summary)

http://augur.osshealth.io:5000/api/unstable/repo-groups/24/aggregate-summary



# Get Fork Count of repos based on repot group
Will get the data based on the repo group id and will display all the reports that are in the data, then let the user select the repo that they want to see and the number of forks will be displayed in a bar graph.

Purpose: to show a developer how many people are working or using a repo.

API: Fork Count (Repo Group) (/repo-groups/:repo_group_id/fork-count)

http://augur.osshealth.io:5000/api/unstable/repo-groups/fork-count
s
