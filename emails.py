import MySQLdb
import cherrypy

import email

import mailbox

import time

from compose import Compose

from readone import ReadOne

from reply import Reply

import html_strings

import utils

from require import require

class Email(object):

    compose = Compose()

    readone = ReadOne()

    reply = Reply()

    @cherrypy.expose
    @require()
    def index(self,sent="False"):

        is_mobile = False

        if "Android" in cherrypy.request.headers['User-Agent'] or "iPhone" in cherrypy.request.headers['User-Agent'] or "iPad" in cherrypy.request.headers['User-Agent']:
            is_mobile = True

        if sent == "False":
            sent_bool = False
        else:
            sent_bool = True

        secrets_file=open("/home/ec2-user/secrets.txt")

        passwords=secrets_file.read().rstrip('\n')

        db_password = passwords.split('\n')[0]

        dbname = "ecommunicate"

        conn = MySQLdb.connect(host='ecommunicate-production.cphov5mfizlt.us-west-2.rds.amazonaws.com', user='browser', passwd=db_password, port=3306)

        curs = conn.cursor()

        curs.execute("use "+dbname+";")

        if sent_bool == False:
            curs.execute("select * from received_emails where username = \""+cherrypy.session.get('_cp_username')+"\" order by received_time desc;")
        else:
            curs.execute("select * from sent_emails where username = \""+cherrypy.session.get('_cp_username')+"\" order by sent_time desc;")

        colnames = [desc[0] for desc in curs.description]

        emails=curs.fetchall()

        if sent_bool == False:
            #use the message factory so that you get MaildirMessages instead of rfc822.Messages
            
            try:
                emailbox = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage,create=False)
            except mailbox.NoSuchMailboxError:
                pass
                
        else: 
            emailbox = mailbox.Maildir('/efsemail/mail/vhosts/ecommunicate.ch-sent/'+cherrypy.session.get('_cp_username')+'/', factory=mailbox.MaildirMessage)

        email_javascript_string = ""

        email_string = ""

        if "emails" in vars():

            for i,msg in  enumerate(emails):

                msg_dict=dict(zip(colnames, msg))

                em = emailbox.get_message(msg_dict["id"])

                email_javascript_string += "var email"+str(i)+" = document.getElementById('email"+str(i)+"');\n"

                email_javascript_string += "email"+str(i)+".addEventListener('mouseover',function(e) { $('#email"+str(i)+"').css('background-color','WhiteSmoke');  } ,  false);\n"

                if not sent_bool:
                    if msg_dict["is_read"]:
                        email_javascript_string += "email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"
                    else:
                        email_javascript_string += "email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','Gold');  } ,  false);\n"
                else:
                    email_javascript_string += "email"+str(i)+".addEventListener('mouseout',function(e) { $('#email"+str(i)+"').css('background-color','White');  } ,  false);\n"


                if sent_bool == False:
                    email_javascript_string += "email"+str(i)+".addEventListener('click',function(e) { window.open('/email/readone/?message_id="+msg_dict["id"]+"','_self')  } ,  false);\n"
                else:    
                    email_javascript_string += "email"+str(i)+".addEventListener('click',function(e) { window.open('/email/readone/?sent=True&&message_id="+msg_dict["id"]+"','_self')  } ,  false);\n"



                if email_string == "":
                    email_string += "<table border = \"1\" width = \"100%\" id=\"emaillist\" style=\"table-layout:fixed\" >"

                if not sent_bool:
                    if msg_dict["is_read"]:
                        email_string += "<tr id=\"email"+str(i)+"\" style=\"background-color:white\">"
                    else:
                        email_string += "<tr id=\"email"+str(i)+"\" style=\"background-color:gold\">"
                else:
                    email_string += "<tr id=\"email"+str(i)+"\" style=\"background-color:white\">"
                    

                if is_mobile:

                    if 'Date' in em:
                        email_string += "<td id=\"table_divide\" style=\"overflow:hidden;max-width:100%;width:100%;white-space:nowrap\" ><div style=\"text-align:right\">"+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+"</div>"


                    if sent_bool:
                        if 'To' in em:
                            if email.utils.parseaddr(em['To'])[0]:
                                email_string += "<b>"+email.utils.parseaddr(em[1]['To'])[0]+"</b>"
                            else:    
                                email_string += "<b>"+email.utils.parseaddr(em['To'])[1]+"</b>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
                    else:
                        if 'From' in em:
                            if email.utils.parseaddr(em['From'])[0]:
                                email_string += "<b>"+email.utils.parseaddr(em['From'])[0]+"</b>"
                            else:
                                email_string += "<b>"+email.utils.parseaddr(em['From'])[1]+"</b>"

                    if 'Subject' in em:    
                        email_string += "<br><i>"+em['Subject']+"</i>"
                    else:
                        email_string += "<br>"

                    if em.is_multipart():
                        if em.get_payload()[0].is_multipart():
                            email_string += "<br>"+em.get_payload()[0].get_payload()[0].get_payload().rstrip('\n')
                        else:
                
                            if em.get_payload()[0].get_payload().rstrip('\n'):
                                email_string += "<br>"+em.get_payload()[0].get_payload().rstrip('\n')
                            else:
                                email_string += "<br>"
                    else:
                        email_string += "<br>"+em.get_payload()

                    email_string += "<br>"

                    email_string += "</td>"


                    email_string += "</tr>"


                else:

                    if sent_bool:
                        if 'To' in em:
                            if email.utils.parseaddr(em['To'])[0]:
                                email_string += "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em[1]['To'])[0]+"</b></td>"
                            else:    
                                email_string += "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['To'])[1]+"</b></td>"
                    #email_string = email_string + email.utils.parseaddr(em[1]['From'])[1]+"<br>"            
                    else:
                        if 'From' in em:
                            if email.utils.parseaddr(em['From'])[0]:
                                email_string += "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['From'])[0]+"</b></td>"
                            else:
                                email_string += "<td style=\"overflow:hidden;max-width:25%;width:25%;white-space:nowrap\"><b>"+email.utils.parseaddr(em['From'])[1]+"</b></td>"

                    if 'Subject' in em:    
                        email_string += "<td style=\"overflow:hidden;max-width:30%;width:30%;white-space:nowrap\"><i>"+em['Subject']+"</i></td>"

                    if em.is_multipart():
                        if em.get_payload()[0].is_multipart():
                            email_string += "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()[0].get_payload()[0].get_payload()+"</td>"
                        else:
                
                            if em.get_payload()[0].get_payload().rstrip('\n'):
                                email_string += "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()[0].get_payload().rstrip('\n')+"</td>"
                            else:
                                email_string += "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\"></td>"
                    else:
                        email_string += "<td style=\"overflow:hidden;max-width:35%;width:35%;white-space:nowrap\">"+em.get_payload()+"</td>"

                    if 'Date' in em:
                        email_string += "<td id=\"table_divide\" style=\"overflow:hidden;max-width:10%;width:10%;white-space:nowrap\" >"+time.strftime("%d %b %H:%M",email.utils.parsedate(em['Date']))+"</td>"


                    email_string += "</tr>"


            if email_string != "":    
                email_string += "</table>"

        curs.close()

        conn.close()
                

        if is_mobile:

            html_string = """
<head>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>
Ecommunicate
</title>
<style>

nav a, button {
    min-width: 48px;
    min-height: 48px;
}

html, body {
    height: 100%;
    width: 100%;
    margin-top:0;
    margin-left:0;
    margin-right:0;
}

a#menu svg {
    width: 40px;
    fill: #000;
}

main {
    width: 100%;
    height: 100%;
}

nav {
    width: 250px;
    height: 100%;
    position: fixed;
    transform: translate(-250px, 0);
    transition: transform 0.3s ease;
}

nav.open {
    transform: translate(0, 0);
}

.header {
    float : right
}

.content {
    padding-left:1em;
    padding-right:1em;
}

</style>

</head>

<body>

<nav id="drawer" style="background-color:LightGrey">

<center><h2 style="margin-top:0">Ecommunicate</h2></center>"""+(html_strings.authenticated_mobile_navigation_menu if utils.is_session_authenticated() else html_strings.not_authenticated_mobile_navigation_menu)+"""

</nav>

<main>

<div style = "width:100%;top:0;left:0;">

<a id="menu">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
    <path d="M2 6h20v3H2zm0 5h20v3H2zm0 5h20v3H2z" />
  </svg>
</a>

<div class = "header">

<h1 style="margin-top:0;margin-bottom:0">Ecommunicate</h1>

</div>

</div>

<div class = "content">

<center>
<h2>Email</h2>
</center>
<br><br>
<table>
<tr>
<td width="150">
<a href="/email/compose/" class="button">Compose</a>
</td>
<td width="150">
<a href="/email/">Received</a>
</td>
<td width="150">
<a href="/email/?sent=True">Sent</a>
</td>
</tr>
</table>
<br><br>

"""+email_string+"""

</div>
</main>

<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 

<script>
"""+email_javascript_string+"""
</script>

<script type="text/javascript">

var menu = document.querySelector('#menu');

var main = document.querySelector('main');

var drawer = document.querySelector('#drawer');

menu.addEventListener('click', function(e) {
    drawer.classList.toggle('open');
    e.stopPropagation();
});

main.addEventListener('click', function() {
    drawer.classList.remove('open');
});

main.addEventListener('touchstart', function() {
    drawer.classList.remove('open');
});

</script>  

</body></html>

"""

        else:

            html_string = """<html>
<head>

"""+html_strings.google_adsense_conversion_tracking_global_site_tag+"""

<style>
a.button {
    -webkit-appearance: button;
    -moz-appearance: button;
    appearance: button;
    padding: 7px;    
    text-decoration: none;
    color: initial;
}
.terminal {
border: none; 
}

.nonheader { width:960px; margin: 80px auto 0px auto;  }   

"""+html_strings.header_style+"""
</style>
<title>Ecommunicate</title>
</head>
<body>
"""+(html_strings.authenticated_header if utils.is_session_authenticated() else html_strings.not_authenticated_header)+"""

<div class = "nonheader">
<center>
<h2>Email</h2>
</center>
<br><br>
<table>
<tr>
<td width="150">
<a href="/email/compose/" class="button">Compose</a>
</td>
<td width="150">
<a href="/email/">Received</a>
</td>
<td width="150">
<a href="/email/?sent=True">Sent</a>
</td>
</tr>
</table>
<br><br>
"""+email_string+"""

</div>

</body>
<script type="text/javascript" src="https://code.jquery.com/jquery-3.1.0.js"></script> 
<script>
"""+email_javascript_string+"""
</script>
        </html>"""

        return html_string
