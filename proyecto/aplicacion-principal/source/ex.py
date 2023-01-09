import paramiko,time,json,pprint
from graphviz import Graph

max_buffer=65535

def clear_buffer(connection):
    if connection.recv_ready():
        return connection.recv(max_buffer)

def grafo():
    g = Graph("Topologia",filename="static/topologia.gv",format='png')
    topologia={"Router":{}}
    usuario='admin'
    password='admin01'
    faltantes={}
    lista=[]



    outputFileName = "Rutas.txt"
    while(True):
        connection=paramiko.SSHClient()
        connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if(len(faltantes) is 0 and len(lista) is 0):
            ip='200.10.10.1'    #gateway conocido
        else:
            llaves=list(faltantes.keys())
            #print(llaves)
            ip=faltantes[llaves[0]]
            del faltantes[llaves[0]]
        connection.connect(ip,username=usuario,password=password,look_for_keys=False,allow_agent=False)
        new_connection=connection.invoke_shell()
        output=clear_buffer(new_connection)
        
        time.sleep(2)
        new_connection.send("terminal length 0\n")
        output=clear_buffer(new_connection)
        #new_connection.send("show running-config | include route\n")
        new_connection.send("show running-config | include hostname\n")

        time.sleep(1)
        output=new_connection.recv(max_buffer)
        pos=output.find('hostname'.encode())
        pos=output.find('hostname'.encode(),pos+2)

        aux=output[pos:pos+50].split()
        routerActual=aux[1].decode()
        g.node(routerActual)
        #print("router actual: ",routerActual)
        #print("Routers Faltantes: ",faltantes)
        #print("Routers conocidos: ",topologia)
        lista.append(routerActual)
        #print(lista)
        new_connection.send("show cdp neighbors detail\n")
        
        time.sleep(1)
        output=new_connection.recv(max_buffer)
        output.decode()
        pos=output.find('Device ID: '.encode())
        topologia["Router"]["id:"+routerActual]=[]
#        print(routerActual)
#        print("Vecinos: ")
        while (pos!=-1):
            aux=output[pos:pos+30].split()
            aux=aux[2].decode()
            aux=aux.split(".")
            routerID=aux[0]
            #print(routerID)
            pos=output.find('IP address: '.encode(),pos)
            aux=output[pos:pos+30].split()
            aux=aux[2].decode()
            aux=aux.split("\r")
            ipSalto=aux[0]
#            print("\tRouter: ",routerID,"--- Salto: ",ipSalto)
            if(routerID not in lista and routerID not in faltantes.keys()):
                faltantes[routerID]=ipSalto
            #print(ipSalto)
            pos=output.find('Device ID: '.encode(),pos)
            topologia["Router"]["id:"+routerActual].append({'enlace':routerID,"ip":ipSalto})
            g.edge(routerActual,routerID)
            new_connection.send("conf t\nusername pirata privilege 15 password pirata\n")
        #print(faltantes)
#        print("\n")
        if(len(faltantes) is 0):
            break
#    g.render("static/topologia.gv",view=True)
    print("\n")
    g.render("static/topologia.gv")