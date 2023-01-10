from flask import Flask, jsonify, redirect, url_for, render_template, request, send_from_directory
from livereload import Server, shell
from main import *
import time
import threading
import os
import sqlite3 as sql
import hashlib
from datetime import date
from datetime import datetime

BLUE = os.path.join('static', 'blue')

user=""
permiso=0
cosultado=0
columna="fecha"

tiempo=180
def ciclo():
	i=1
	global tiempo
	while(1<=10):
		#print("hola")
#		grafo()
		crearG()
		bloquea.acquire()
		try:
			time.sleep(tiempo)
		finally:
			bloquea.release()

			
app= Flask(__name__)
app.config['UPLOAD_FOLDER'] = BLUE


@app.route('/')
def login():
	return render_template("login.html")


@app.route('/favicon.ico')
def favicon():
	#print("hola\n")
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/menu',  methods=["GET", "POST"])
def princ():
	global user
	global permiso
	if request.method == 'POST':
		try:
			nm = request.form['nm']
			ps = request.form['ps']
			
			h = hashlib.sha1(ps.encode('utf-8'))
			a=h.hexdigest()
			with sql.connect("proyecto.db") as con:
				print("conexion exitosa\n")
				cur = con.cursor()
				string="SELECT contrasenia FROM usuarios WHERE (nombre="+"'"+nm+"')"
				cur.execute(string)
				res=cur.fetchall()
				s=res[0]
				b=s[0]
				string="SELECT permiso FROM usuarios WHERE (nombre="+"'"+nm+"')"
				cur.execute(string)
				resu=cur.fetchall()
				t=resu[0]
				c=t[0]
				con.commit()
		except:
			b="error"
			con.rollback()
			print("algo salio mal\n")
		finally:
			print(b)
			print(a)
			if (a==b):
				user=nm
				permiso=c

				return render_template("index.html")
			else:
				return render_template("login.html")
			con.close()
	else:
		return render_template("index.html")


@app.route('/topologia',  methods=["GET", "POST"])
def topo():
	#print("hola\n")
#	full_filename1 = os.path.join(app.config['UPLOAD_FOLDER'], 'router.svg')
#	full_filename2 = os.path.join(app.config['UPLOAD_FOLDER'], 'client.svg')
#	return render_template("topo.html", router = full_filename1, cliente = full_filename2)
#	return render_template("TA.html")
	global tiempo
	if request.method == 'POST':
		if(request.form['signup']=='Enviar'):
			resp=request.form['name']
	#		print("tiempo "+resp+" seg")
			bloquea.acquire()
			try:
				tiempo=int(resp)
				print("Tiempo de deteccion actualizado a "+tiempo+" seg")
			finally:
				bloquea.release()
				return render_template("TA.html")
		elif(request.form['signup']=='Forzar deteccion'):
			crearG()
			return render_template("TA.html")
	else:
		return render_template("TA.html")


@app.route('/dispositivos',  methods=["GET", "POST", "PUT"])
def disp():
	#print("hola\n")
	global user
	global permiso
	if request.method == 'GET':
		
		host = obtHost()
		return render_template("disp.html", hosts=host)

#		if request.form['signup'] == 'Info':

#			obtInfoU()
			
#			return render_template("disp.html", hosts=host)
#		else:
#			return render_template("disp.html", hosts=host)
	elif request.method == 'POST':
		
		router = request.form.get("routers")
		nm = request.form['name']
		ps = request.form['pss']
		pr = request.form['prv']
		host = obtHost()

		if(permiso==1):
			try:
				if router == "null":
					print("Se debe seleccionar un Router/s")
				else:
					with sql.connect("proyecto.db") as con:
						print("conexion a la BD exitosa")
						cur = con.cursor()
					
						if(request.form['signup']=='Crear'):
	#							print("vamos a crear")
							if(len(nm)!=0 and len(ps)!=0 and len(pr)!=0):
								today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
								accion="Creacion de usuario "+nm+" en [ "+router+" ]"+" dispositivo de red"
								cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))
								crearU(router, nm, ps, pr)
							else:
								print("Todos los campos deben estar llenos.")
						elif(request.form['signup']=='Modificar'):
	#							print("vamos a modificar")
							if(len(nm)!=0 and len(ps)!=0 and len(pr)!=0):
								today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
								accion="Modificacion de usuario "+nm+" en [ "+router+" ]"+" dispositivo de red"
								cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))						
								modificarU(router, nm, ps, pr)
							else:
								print("Todos los campos deben estar llenos.")
						elif(request.form['signup']=='Eliminar'):
	#							print("eliminamos")
							if(len(nm)!=0):
								today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
								accion="Eliminar usuario "+nm+" en [ "+router+" ]"+" dispositivo de red"
								cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))
								eliminarU(router, nm)
							else:
								print("Se necesita ingresar el usuario a eliminar.")
							#print(rows)
						con.commit()
			except:
				con.rollback()
				print("Algo salio mal\n")
			finally:
				return render_template("disp.html", hosts=host)
		else:
			print("Tu no puedes hacer esto")
			return render_template("error.html")
	else:
		host = obtHost()
		if request.form['signup'] == 'Info':

			obtInfoU()
			
			return render_template("disp.html", hosts=host)
#		return render_template("disp.html")


@app.route('/enrutamiento', methods=["GET", "POST"])
def enr():
		#print("hola\n")
		global user
		global permiso
		if permiso==0:
			dis = "block"
		else:
			dis = "none"
		if request.method == 'POST':
			try:
				uss = request.form['uss']
				pss = request.form['pss']
				ER = request.form.get("tipoER")

				if ER == "null":
					print("Se debe seleccionar un tipo de Enrutamiento")
				else:
					with sql.connect("proyecto.db") as con:
						print("Conexion a la BD exitosa")
						cur= con.cursor()
						if(request.form['signup']=='default'):
							today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
							accion="Se levanto el Enrutamiento "+ER+" en la red"
							cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))
							enrutamiento(permiso,uss,pss,ER)
						con.commit()
			except:
				con,rollback()
				print("algo salio mal\n")
			finally:
				return render_template("enru.html", disp=dis)
		else:
			return render_template("enru.html", disp=dis)


@app.route('/usuarios',  methods=["GET", "POST"])
def user():
		#print("hola\n")
		global user
		global permiso
		if request.method == 'POST':
			nm = request.form['name']
			print(nm)
			ps = request.form['pass']
			cr = request.form['email']
			h = hashlib.sha1(ps.encode('utf-8'))
			a=h.hexdigest()
			admin = request.form.getlist('AU')
			uss= request.form.getlist('AO')
			if(permiso==1):
				try:
					with sql.connect("proyecto.db") as con:
						print("conexion exitosa")
						con.row_factory=sql.Row
						cur = con.cursor()
						if(request.form['signup']=='Crear'):
							print("vamos a crear")
							if(len(nm)!=0 and len(ps)!=0 and len(cr)!=0):
								if(len(admin)==1):
									cur.execute("INSERT INTO usuarios(nombre,correo,permiso,contrasenia) VALUES (?,?,?,?)",(nm,cr,1,a))
								else:
									cur.execute("INSERT INTO usuarios(nombre,correo,permiso,contrasenia) VALUES (?,?,?,?)",(nm,cr,0,a))
								today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
								accion="Creacion de usuario "+nm+" para acceso a la pagina"
								cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))

						elif(request.form['signup']=='Modificar'):
							print("vamos a modificar")
							if(len(nm)!=0 and len(ps)!=0 and len(cr)!=0):
								if(len(admin)==1):
									cur.execute("UPDATE usuarios SET correo=?, permiso=?, contrasenia=? WHERE nombre=?",(cr,1,a,nm))
								else:
									cur.execute("UPDATE usuarios SET correo=?, permiso=?, contrasenia=? WHERE nombre=?",(cr,0,a,nm))
								today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
								accion="Modificacion de usuario "+nm+" para acceso a la pagina"
								cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))

						elif(request.form['signup']=='Eliminar'):
							print("eliminamos")
							if(len(nm)!=0 and nm != 'admin'):
								string="DELETE FROM usuarios WHERE (nombre="+"'"+nm+"')"
								cur.execute(string)
								today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
								accion="Eliminar usuario "+nm+" para acceso a la pagina"
								cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,?,?)",(user,accion,today))
						cur.execute("SELECT nombre,correo FROM usuarios")
						rows=cur.fetchall()
						#print(rows)
						con.commit()
				except:
					con.rollback()
					print("algo salio mal\n")
				finally:
					return render_template("user.html", rows=rows)
			else:
				print("tu no puedes hacer esto")
				return render_template("error.html")

		else:
			try:
				with sql.connect("proyecto.db") as con:
					con.row_factory = sql.Row
					cur = con.cursor()
					cur.execute("SELECT nombre,correo FROM usuarios")
					rows=cur.fetchall()
					con.commit()
			except:
				con.rollback()
			finally:
				return render_template("user.html", rows=rows)


@app.route('/bitacora', methods=["GET", "POST"])
def bita():
		#print("hola\n")
		global consultado
		global columna
		if request.method == 'POST':
			dis="block"
			columna2= request.form['signup']
			if(columna2 != columna):
				columna=columna2
				consultado=0
			try:
				with sql.connect("proyecto.db") as con:
					con.row_factory=sql.Row
					cur = con.cursor()
					if(consultado==0):
						orden="SELECT * FROM bitacora ORDER BY "+columna+" DESC"
						consultado=1
					elif(consultado==1):
						orden="SELECT * FROM bitacora ORDER BY "+columna+" ASC"
						consultado=0
					cur.execute(orden)
					rows=cur.fetchall()
					com.commit()
			except:
				con.rollback()
			finally:
				return render_template("bitac.html", rows=rows, disp=dis)
		else:
			dis="none"
			try:
				with sql.connect("proyecto.db") as con:
					con.row_factory=sql.Row
					cur = con.cursor()
					cur.execute("SELECT * FROM bitacora ORDER BY fecha DESC")
					consultado=1
					rows=cur.fetchall()
					com.commit()
			except:
				con.rollback()
			finally:
				return render_template("bitac.html", rows=rows, disp=dis)


@app.route('/monitoreo')
def data():
		#print("hola\n")
		host = obtHost()
		return render_template("data.html", hosts=host)


@app.route('/alertas', methods=["GET", "POST"])
def alerts():
		#print("hola\n")
		global user
		global permiso
		if request.method == 'POST':
			try:
				with sql.connect("proyecto.db") as con:
					cur= con.cursor()
					if(request.form['signup']=='Aceptar')	:
						today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
						cur.execute("INSERT INTO bitacora(usuario,accion,fecha) VALUES (?,'Configuracion de alertas',?)",(user,today))
					con.commit()
			except:
				con,rollback()
				print("algo salio mal\n")
			finally:
				return render_template("alertas.html")
		else:
			return render_template("alertas.html")


if __name__ == '__main__':
	print('Iniciando proyecto final...')
	bloquea=threading.Lock()
	hilo=threading.Thread(target=ciclo)
	hilo.start()
#	app.run(debug=True, port=5500)
	server=Server(app.wsgi_app)
	server.watch('static/topologia.gv.png', shell('make html'))
	server.serve()