import smtplib, email, os, schedule, re, ssl, time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

### Compiled Regexes ###
email_regex = re.compile(r"^[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+$")
time_regex = re.compile(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")

### Starts with a blank list of emails ###
list_of_emails = []

### Default Values Here ###
email_subject = "Daily Report"
from_email = "jacob.jackson.python.course@gmail.com"
app_password = "hdvn qmpb qxay vzmw"
email_body = "Here is your daily report, attached as a PDF.\n\n"
report_file = "report.pdf"
time_to_send = "08:00"

def printlog(string): #a function that both prints and logs to a file any message we want
    log_string = f"{datetime.now()} {string}" #prefixes the message with the time/date stamp
    print(log_string) #prints it
    try:
        with open("log.txt", "a") as logf: #opens up a log file named "log.txt" for appending
            logf.write(log_string + "\n") #writes it with a newline character at the end
    except Exception as e: #Any error that occurs during logging is printed only
        print("Ooops, an error occured in writing to log file: ", e)

def get_list_of_emails():
    while True:
        email_in = input("Input a recipient's email address (done to end): ")
        if email_in == "done":
            break #break out of while loop, user entered "done"
        elif re.match(email_regex, email_in): #if the user entered a valid email address
            list_of_emails.append(email_in) #append the email to the list_of_emails
        else: #if the user did not enter a valid email address
            printlog(f"Invalid e-mail address entered!")
            continue #ask again
    printlog(f"Will be sending to {list_of_emails}") #Logs/shows the list_of_emails when user enters "done"

def get_subject_of_email():
    global email_subject
    input_string = input("Enter subject of email (return for default): ")
    if input_string != "": #if the user entered anything at all
        email_subject = input_string  #save the input in email_subject
    else:  #otherwise, preserve the default value of email_subject
        printlog(f"Going with default email subject")

def get_body_of_email():
    global email_body
    input_string = input("Enter body of email (return for default): ")
    if input_string != "": #if the user entered anything at all
        email_body = input_string #save the input in email_body
    else: #otherwise, preserve default value of email_body
        printlog(f"Going with default email body")

def get_from_email():
    global from_email
    while True:
        input_string = input("Enter your GMAIL email address (return for default - recommended): ")
        if re.match(email_regex, input_string): #if the user enters a valid email address
            from_email = input_string   #save the input in the from_email variable, replacing the default
            break #break out of the while loop, we're done here
        elif input_string == "": #if the user hit return
            printlog(f"Going with default from email address")
            break    #preserve the default value of from_email
        else:  #if invalid email is entered
            printlog(f"Invalid e-mail address entered!")
            continue  #ask again

def get_app_password():
    global app_password
    input_string = input("Enter your GMAIL app password (return for default - recommended): ")
    if input_string != "" and not input_string.isspace(): #if anything is entered that's not whitespace
        app_password = input_string #store the input as the new app_password
    else: #if the user hit return or entered whitespace, preserve the original value of app_password
        printlog(f"Going with default GMAIL app password")

def get_report_file(): #Get the report file from the user
    global report_file
    while True:
        input_string = input("Enter filename or path of report to attach (return for default): ")
        if input_string.isspace() or input_string == "": #if user hits return or enters only whitespace
            printlog(f"Going with default file 'report.pdf' in current directory")
            break  #report_file is preserved as its original, default value
        elif os.path.isfile(input_string):  #if the input is a valid file
            report_file = input_string  #change report_file to the valid input
            break  #leave the while loop, we're done here
        else:  #if file didn't exist
            printlog(f"File {input_string} does not exist, sorry.")
            continue  #ask for a filename or path again, becuase the file didn't exist

def get_time_to_send(): #Get the time when the emails should be sent each day from the user
    global time_to_send
    while True:
        input_string = input("Enter time to send email daily (HH:MM) (return for default): ")
        if re.match(time_regex, input_string): #if input matches HH:MM format
            time_to_send = input_string #replace default value of time_to_send with input
            break #break out of the while loop, we're done here
        elif input_string == "": #user entered return, going with default time
            printlog(f"Going with default send time, {time_to_send}")
            break #preserve default value of time_to_send
        else:   #user did not enter a valid time
            print(f"Invalid time to send, use HH:MM format")
            continue #ask again

def send_emails(): #Do all the setup/creation of the email, and sends a copy to each recipient
    try:
        printlog(f"Sending emails right now...")
        string_list_of_emails = ", ".join(list_of_emails) #Create email-friendly list of emails
        printlog(f"Creating email for {string_list_of_emails}...")
        message = MIMEMultipart()   #Create email message ready for an attachment

        ### Load in values from get_ functions or their default values ###
        message["From"] = from_email
        message["To"] = string_list_of_emails
        message["Subject"] = email_subject
        message.attach(MIMEText(email_body + "\n\n", "plain")) #Plain text body

        printlog(f"Attaching file {report_file} to email...")

        with open(report_file, "rb") as attachment:     #Open report file in binary mode
            part = MIMEBase("application", "octet-stream") #Set up the MIME attachment
            part.set_payload(attachment.read()) #Read in the report file
        encoders.encode_base64(part) #encode as ascii
        part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(report_file)}") #set filename of report
        message.attach(part) #attach to email message

        text = message.as_string() #get the whole message as a string, called text

        printlog(f"Connecting to SMTP server...")

        context = ssl.create_default_context() #Create context for SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server: #set up connection to smtp server
            server.login(from_email, app_password) #log in to smtp server
            for to_email_address in list_of_emails: #for every email recipient
                server.sendmail(from_email, to_email_address, text) #send message to recipient
                printlog(f"Sent email to {to_email_address}")

        printlog(f"Scheduled to email again at {time_to_send} tomorrow.") #Remind user when next email will be sent

    except Exception as e:
        printlog(f"Ooops, an error occurred: {e}")


def main():
    try:
        printlog(f"Automated Emailer Starting Up...")
        get_list_of_emails()
        get_subject_of_email()
        get_body_of_email()
        get_from_email()
        get_app_password()
        get_report_file()
        get_time_to_send()

        printlog(f"Scheduled to email at {time_to_send} every day.")

        schedule.every().day.at(time_to_send).do(send_emails) #use scheduler to send emails at given time

        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        printlog(f"Ooops, an error occured: {e}")


if __name__ == "__main__":
    main()
