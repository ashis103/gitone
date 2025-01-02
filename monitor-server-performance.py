import paramiko
import socket
import time
import logging
import datetime
import re

client = None
shell = None
#Login to the servers
def login(hostn, uname, pwd):
    global client
    global shell
    client = paramiko.SSHClient()
    try:
        #logging.info("-------------Trying to establish connection with server-------------")
        #logging.info("IPAddres : " + hostn + ", Username : " + uname)
        #logging.info("Establishing ssh connection")
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostn ,username=uname,password=pwd)
        #logging.info("-------------Successfully connected to Server-------------")
        shell = client.invoke_shell()
    except paramiko.AuthenticationException as authenticationException:
        #logging.error("Authentication failed, please verify your credentials : %s" % authenticationException)
        raise Exception("Authentication failed, please verify your credentials")
    except socket.error as e:
        #logging.error("Communication problem : %s" % e)
        raise Exception("Entered IP Address is wrong")
    except paramiko.BadHostKeyException as badHostKeyException:
        #logging.error("Unable to verify server's host key: %s" % badHostKeyException)
        raise Exception("Unable to verify server's host key")
    except paramiko.SSHException as sshException:
        #logging.error("Unable to establish SSH connection: %s" % sshException)
        raise Exception("Unable to establish SSH connection")
    except Exception as e:
        #logging.error("Something went wrong : %s" % e)
        raise Exception("Something went wrong")

#Function to execute commands on the servers
def exec_cmd(command):
    #logging.info("Executing command : "+command)
    stdin,stdout, stderr = client.exec_command(command)
    result = stderr.read().decode("utf-8")
    msg = stdout.read().decode("utf-8")
    #print(result)
    if len(result) > 0:
        return result
    else:
        return msg

#Function to execute commands on a shell
def exec_shell(command,sleeptime = 1):
    global shell
    #logging.info("Executing command : "+command)
    command = command+"\n"
    shell.send(command)
    time.sleep(sleeptime)
    receive_buffer = shell.recv(9999).decode("utf-8")
    return receive_buffer

#Function to determine flavor of the servers
def server_flavour(command_output):
    if "Linux" in command_output:
        #print("it is Linux")
        actual_output =linux_server()
    elif "AIX" in command_output:
        #print("it is AIX server")
        actual_output= aix_server()
    else:
        raise Exception("Flavour is neither Linux or Solaris")
    return actual_output


#Function to close the server connection
def clean_up():
    client.close()
    #logging.info("-------------Successfully closed Server connection-------------")


#Function defining the conditions for color coding of "ps -eo pcpu,pid,user,args | sort -k 1 -r | head -10" command for linux and solaris servers
#Function defining the conditions for color coding of "ps aux | head -1; ps aux | sort -rn +2 | head -10" command for AIX server
def ps_html(var2):
    list2 = var2.split("\n")
    s = re.findall(r'\S+', list2[0])
    index_val2 = s.index('%CPU')
    #print(index_val2)
    list2 = [s for s in list2 if s != '']
    fun_html = "<table><tr><td><pre><h3>" + list2[0] + "</h3></pre></td></tr>"
    for j in list2[1:]:
        i = re.findall(r'\S+', j)
        comp = float(i[index_val2])
        print(comp)
        if (comp >= 90):
            fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre><h3>" + j + "</h3></pre></td></tr>"
            #print("90", i)
        elif (comp >= 80 and comp < 90):
            #print("80 to 90", i)
            fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre><h3>" + j + "</h3></pre></td></tr>"
        else:
            #print("less than 80", i)
            fun_html = fun_html + "<tr><td><pre><h3>" + j + "</h3></pre></td></tr>"
    fun_html = fun_html + "</table>"
    return fun_html

#Function defining the conditions for color coding of "df -h" command for linux servers
def df_html(var1):
    list1 = var1.split("\n")
    s = re.findall(r'\S+', list1[0])
    index_val1 = s.index('Use%')
    #print(index_val1)
    list1 = [s for s in list1 if s != '']
    fun_html = "<table><tr><td><pre>" + list1[0] + "</pre></td></tr>"
    #print(list1)
    for j in range(len(list1)):
        i = re.findall(r'\S+', list1[j])
        if len(i) == 6:
            comp = float(i[index_val1].replace('%', ""))
            #print(i, comp)
            if (comp >= 90):
                fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre>" + list1[j] + "</pre></td></tr>"
                #print("90", i)
            elif (comp >= 80 and comp < 90):
                #print("80 to 90", i)
                fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre>" + list1[j] + "</pre></td></tr>"
            else:
                #print("less than 80", i)
                fun_html = fun_html + "<tr><td><pre>" + list1[j] + "</pre></td></tr>"
        elif len(i) == 1:
            k = list1[j] + list1[j + 1]
            l = re.findall(r'\S+', k)
            comp = float(l[index_val1].replace('%', ""))
            #print(l, comp)
            if (comp >= 90):
                fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre>" + list1[j] + "</pre></td></tr>"
                fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre>" + list1[
                    j + 1] + "</pre></td></tr>"
                #print("90", i)
            elif (comp >= 80 and comp < 90):
                #print("80 to 90", i)
                fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre>" + list1[j] + "</pre></td></tr>"
                fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre>" + list1[
                    j + 1] + "</pre></td></tr>"
            else:
                #print("less than 80", i)
                fun_html = fun_html + "<tr><td><pre>" + list1[j] + "</pre></td></tr>"
                fun_html = fun_html + "<tr><td><pre>" + list1[j + 1] + "</pre></td></tr>"

    fun_html = fun_html + "</table>"
    return fun_html

#Function defining the conditions for color coding of "df -g" command for AIX servers
def df_html_aix(var1):
    list1 = var1.split("\n")
    s = re.findall(r'\S+', list1[0])
    index_val1 = s.index('%Used')-1
    #print(index_val1)
    list1 = [s for s in list1 if s != '']
    fun_html = "<table><tr><td><pre>" + list1[0] + "</pre></td></tr>"
    #print(list1)
    for j in range(len(list1)):
        i = re.findall(r'\S+', list1[j])
        if len(i) == 7:
            # checking if value is '-'
            if (i[index_val1] != "-"):
                comp = float(i[index_val1].replace('%', ""))
                #print(i, comp)
                if (comp >= 90):
                    fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre>" + list1[j] + "</pre></td></tr>"
                    #print("90", i)
                elif (comp >= 80 and comp < 90):
                    #print("80 to 90", i)
                    fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre>" + list1[j] + "</pre></td></tr>"
                else:
                    #print("less than 80", i)
                    fun_html = fun_html + "<tr><td><pre>" + list1[j] + "</pre></td></tr>"
            else:
                fun_html = fun_html + "<tr><td><pre>" + list1[j] + "</pre></td></tr>"

        elif len(i) == 1:
            k = list1[j] + list1[j + 1]
            l = re.findall(r'\S+', k)
            # checking if value is '-'
            if (i[index_val1] != "-"):
                comp = float(l[index_val1].replace('%', ""))
                #print(l, comp)
                if (comp >= 90):
                    fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre>" + list1[j] + "</pre></td></tr>"
                    fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre>" + list1[
                        j + 1] + "</pre></td></tr>"
                    #print("90", i)
                elif (comp >= 80 and comp < 90):
                    #print("80 to 90", i)
                    fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre>" + list1[j] + "</pre></td></tr>"
                    fun_html = fun_html + "<tr><td style='background-color:#FFFF00'><pre>" + list1[
                        j + 1] + "</pre></td></tr>"
                else:
                    #print("less than 80", i)
                    fun_html = fun_html + "<tr><td><pre>" + list1[j] + "</pre></td></tr>"
                    fun_html = fun_html + "<tr><td><pre>" + list1[j + 1] + "</pre></td></tr>"

            else:
                fun_html = fun_html + "<tr><td><pre>" + list1[j] + "</pre></td></tr>"
                fun_html = fun_html + "<tr><td><pre>" + list1[j + 1] + "</pre></td></tr>"

    fun_html = fun_html + "</table>"
    return fun_html

#Function defining the conditions for color coding of "uptime" command for linux and aix servers
def uptime_html(var):
    actual_output = ''
    list = var.split(" ")
    if ('days,' in list):
        days = int(list[list.index('days,') - 1])
    elif ('day(s),' in list):
        days = int(list[list.index('day(s),') - 1])
    elif ('day,' in list):
        days = int(list[list.index('day,') - 1])
    else:
        days = 0
    #print(days)
    if (days == 1 or days == 2):
        actual_output += "<table><tr><td style='background-color:#FFFF00'><pre><h3>" + var + "</h3></pre></td></tr></table>"
    elif (days == 0):
        actual_output += "<table><tr><td style='background-color:#FF0000'><pre><h3>" + var + "</h3></pre></td></tr></table>"
    else:
        actual_output += "<table><tr><td style='background-color:#FFFFFF'><pre><h3>" + var + "</h3></pre></td></tr></table>"
        #print(var)
    return actual_output

#Function defining the conditions for color coding of "vmstat -v |grep -w 'computational pages' |awk '{print $1}'" command for aix servers
def vmstat_aix_html(vmstat_aix_var):
    if float(vmstat_aix_var) > 80:
        fun_html="<table><tr><td style='background-color:#FF0000'><pre><h3>" + vmstat_aix_var + "</h3></pre></td></tr></table>"
    else:
        fun_html="<table><tr><td><pre><h3>" + vmstat_aix_var + "</h3></pre></td></tr></table>"
    return fun_html

#Function defining the conditions for color coding of "svmon -G -O unit=MB" command for aix servers
def svmon_aix_html(svmon_aix_var):
    svmon_aix_list = svmon_aix_var.split("\n")
    print(svmon_aix_list)
    svmon_aix_list = [s for s in svmon_aix_list if s != '']
    print(svmon_aix_list)
    s = re.findall(r'\S+', svmon_aix_list[2])
    index_val_free= s.index('free')
    print(index_val_free)
    print(svmon_aix_list)
    fun_html = "<table>"
    for j in svmon_aix_list[:3]:
        fun_html=fun_html+"<tr><td><pre><h3>" + j + "</h3></pre></td></tr>"
    i = re.findall(r'\S+', svmon_aix_list[3])
    print(type(i[index_val_free+1]))
    comp_svmon_aix=float(i[index_val_free+1])
    print(comp_svmon_aix)
    if comp_svmon_aix <= 1024:
        fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre><h3>" + svmon_aix_list[3] + "</h3></pre></td></tr>"
    else:
        fun_html = fun_html + "<tr><td><pre><h3>" + svmon_aix_list[3] + "</h3></pre></td></tr>"
    for j in svmon_aix_list[4:]:
        fun_html=fun_html+"<tr><td><pre><h3>" + j + "</h3></pre></td></tr>"
    fun_html=fun_html+"<tr><td><pre><h3>" + "Available Free Memory: "+str(comp_svmon_aix) + "</h3></pre></td></tr>"
    fun_html = fun_html + "</table>"
    return fun_html
def rhel_version_check():
    rhel_version_list=exec_cmd('cat /etc/redhat-release').split(' ')
    rhel_version=int(rhel_version_list[rhel_version_list.index('release')+1][0])
    print(rhel_version)
    return rhel_version

def mem_usage_html(mem_usage_var):
    mem_usage_list=mem_usage_var.split('=')
    mem_usage=float(mem_usage_list[1].replace('%',''))
    fun_html = "<table>"
    if mem_usage >= 80:
        fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre><h3>" + mem_usage_var + "</h3></pre></td></tr>"
    else:
        fun_html = fun_html + "<tr><td><pre><h3>" + mem_usage_var + "</h3></pre></td></tr>"
    fun_html = fun_html + "</table>"
    return fun_html

def idle_cpu_html(idle_cpu_var):
    idle_cpu_list=idle_cpu_var.split(',')
    print(idle_cpu_list)
    for i in idle_cpu_list:
        print(i)
        if 'id' in i:
            idle_cpu=float(i.replace(' id',''))
    print(idle_cpu)
    fun_html = "<table>"
    if idle_cpu <= 20:
        fun_html = fun_html + "<tr><td style='background-color:#FF0000'><pre><h3>" + idle_cpu_var + "</h3></pre></td></tr>"
    else:
        fun_html = fun_html + "<tr><td><pre><h3>" + idle_cpu_var + "</h3></pre></td></tr>"
    fun_html = fun_html + "</table>"
    return fun_html

#Function defining various commands to be executed and colour coding to be done for Linux Servers
def linux_server():
    try:
        actual_output = "<h2> SERVER PERFORMANCE REPORT On " + str(
            datetime.datetime.now().strftime("%d/%m/%Y")) + " " + str(
            datetime.datetime.now().strftime("%I:%M:%S %p")) + "</h2><br/>"
        actual_output = "<h2> SERVER PERFORMANCE REPORT On "+str(datetime.datetime.now().strftime("%d/%m/%Y"))+" "+str(datetime.datetime.now().strftime("%I:%M:%S %p"))+"</h2><br/>"

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Host Name: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('hostname')
        actual_output += "<table><tr><td><pre><h3>" + str(cmd) + "</h3></td></tr></table><br/>"

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'>  Server Uptime:  </th></tr></tbody></table><br/>"
        cmd = exec_cmd('uptime')
        actual_output = actual_output + uptime_html(cmd)

        rhel_version=rhel_version_check()
        if rhel_version==5 or rhel_version==6:
            actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Memory: </th></tr></tbody></table><br/>"
            cmd = exec_cmd("MEM_USAGE=$(U=`/usr/bin/free -m | grep "+" | awk {'print $3'}`;T=`/usr/bin/free -m | grep \"Mem\"| awk {'print $2'}`;echo \"scale=2;$U/$T*100\" |bc);echo MEM_USAGE=\"${MEM_USAGE}%\"")
            actual_output = actual_output + mem_usage_html(cmd)
        elif rhel_version==7:
            actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Memory: </th></tr></tbody></table><br/>"
            cmd = exec_cmd("MEM_USAGE=$(U=`/usr/bin/free -m | grep \"Mem\" | awk {'print $3'}`;T=`/usr/bin/free -m | grep \"Mem\"| awk {'print $2'}`;echo \"scale=2;$U/$T*100\" |bc);echo MEM_USAGE=\"${MEM_USAGE}%\"")
            actual_output = actual_output + mem_usage_html(cmd)
        else:
            actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Memory: </th></tr></tbody></table><br/>"
            actual_output += "<table><tr><td><pre><h3>The Rhel version is neither 5,6 or 7</h3></td></tr></table><br/>"

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Top 5 Memory consuming: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('ps -eo pmem,pid -o comm | sort -k1nr | head -5')
        actual_output += "<table><tr><td><pre><h3>" + str(cmd) + "</h3></td></tr></table><br/>"

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Idle CPU: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('COLUMNS=150 top  -bc -n 1|grep  "%Cpu"|grep -v grep')
        actual_output = actual_output + idle_cpu_html(cmd)

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Top 5 CPU consuming: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('ps -eo pcpu,pid -o comm | sort -k1nr | head -5')
        actual_output += "<table><tr><td><pre><h3>" + str(cmd) + "</h3></td></tr></table><br/>"

    except Exception as ex:
        print(str(ex))
        raise Exception("Error in Health-Check Command Run On The Server")
    return actual_output

#Function defining various commands to be executed and colour coding to be done for AIX Servers
def aix_server():
    try:
        actual_output = "<h2> SERVER PERFORMANCE REPORT On " + str(
            datetime.datetime.now().strftime("%d/%m/%Y")) + " " + str(
            datetime.datetime.now().strftime("%I:%M:%S %p")) + "</h2><br/>"
        actual_output = "<h2> SERVER PERFORMANCE REPORT On "+str(datetime.datetime.now().strftime("%d/%m/%Y"))+" "+str(datetime.datetime.now().strftime("%I:%M:%S %p"))+"</h2><br/>"

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Host Name: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('hostname')
        actual_output += "<table><tr><td><pre><h3>" + str(cmd) + "</h3></td></tr></table>"

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'>  Server Uptime:  </th></tr></tbody></table><br/>"
        cmd = exec_cmd('uptime')
        actual_output = actual_output + uptime_html(cmd)

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Computational Memory Percentage: </th></tr></tbody></table><br/>"
        cmd = exec_cmd("vmstat -v |grep -w 'computational pages' |awk '{print $1}'")
        actual_output = actual_output + vmstat_aix_html(cmd)

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Free Memory: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('svmon -G -O unit=MB')
        actual_output = actual_output + svmon_aix_html(cmd)

        actual_output += "<table id='fragmentation'><tbody class='_tbody'><tr><th align = 'left'> Check CPU Load: </th></tr></tbody></table><br/>"
        cmd = exec_cmd('ps aux | head -1; ps aux | sort -rn +2 | head -10')
        actual_output = actual_output + ps_html(cmd)

    except Exception as ex:
        print(str(ex))
        raise Exception("Error in Health-Check Command Run On The Server")
    return actual_output

def main():
    # hostname='10.207.231.26'#sys.argv[1]
    server_list = []
    f = open('Monitor_Server_Performance.txt', "r")
    data_list = f.read().split('\n')
    # data_list=list(filter(None,data_list))
    data_list = [x for x in data_list if x != '' and x != '\r']
    data_list = [x.replace('\r', '') for x in data_list]
    for line in data_list[1:]:
        server_list.append(line)
    print(server_list)

    #Base HTML page code
    actual_output = "<html><head><title>HEALTH CHECK REPORT</title>"
    actual_output += """<style>
                        body{
                        margin=0px;
                        padding=0px;
                        font-family:'Trebuchet MS', Arial, Helvetica, sans-serif;
                        }
                        h2 {
                        font-size: 1.1em;
                        text-align:center;
                        padding-top:5px;
                        padding-bottom:4px;
                        margin-top:1.5em;
                        border-bottom: 2px solid #bbb;
                        }
                        #fragmentation
                        {
                        width:100%;
                        border-collapse:collapse;
                        font-family:'Trebuchet MS', Arial, Helvetica, sans-serif;
                        }
                        #fragmentation td, #fragmentation th
                        {
                        font-size:1em;
                        padding:3px 7px 2px 7px;
                        }
                        #fragmentation th
                        {
                        font-size:1.1em;
                        text-align:left;
                        padding-top:5px;
                        padding-bottom:4px;
                        background-color:#8baad3;
                        color:#000000;
                        }
                        #fragmentation tr.alt td
                        {
                        color:#000000;
                        background-color:#EAF2D3;
                        }
                        </style></head><body>"""
    #traversing through each server and calling the login,execute command and appending the output to Base HTML
    for val in server_list:
        try:
            server_details = val.split(',')
            # Login to the given server
            login(server_details[0], server_details[1], server_details[2])
            print(server_details[0], server_details[1], server_details[2])
            #Execute the command to check the server type
            server_output=exec_shell('uname -a')
            #Report of given server same in each_server_html
            each_server_html = server_flavour(server_output)
            #All reports are consolidated to give a final report
            actual_output = actual_output + each_server_html
        except Exception as ex:
            actual_output += "<h2> SERVER PERFORMANCE REPORT On "+str(datetime.datetime.now().strftime("%d/%m/%Y"))+" "+str(datetime.datetime.now().strftime("%I:%M:%S %p"))+"</h2><br/>"
            actual_output += "<table><tr><td><pre><h3>Error with hostname: " + server_details[0] + "<br/>Error is : " + str(ex) +"</h3></td></tr></table><br/></body></html>"

    f=open('Monitor_Server_Performance.html','w')
    f.write(actual_output)
    f.close()
main()
