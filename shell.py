import cmd, sys
import editor as e
import reproductor as r
import almacenamiento as a
MENSAJE=(" Bienvenido a mi FIUBA Music editor.\n"+
" Antes de activar los tracks debe crear al menos una marca.\n"+
" Cuando carga un archivo elimina todo lo que este en memoria.\n"+
" Ingrese help o ? para listar los comandos.\n")
def es_entero(n):
	"""Recibe y devuelve un booleano si es \n
		->n(int ó str): es el valor validarse como entero"""
	if type(n) == int and n >= 0:
		return True
	return n.isdigit() and int(n) >= 0
def validar_parametro(argumento, max=None):
	"""Recibe un argumento y si cumple las condiciones lo devulve (int)\n
	Caso contrario devulve None.\n
		->argumento(str)\n
		->max(int): opcional\n"""
	if es_entero(argumento):
		argumento = int(argumento)
		if max is not None:
			if argumento < max:
				return argumento
			else:
				print("Se ingreso un numero mayor que ",max)
				return None
		else:
			return argumento
	else:
		print("Lo ingresado no es un numero")
		return None
class _Mark():
	"""Representacion de una marca."""
	def __init__(self, duracion):
		"""Constructor"""
		self.duracion = duracion
		self.tracks = {}
class Shell(cmd.Cmd):
	intro = MENSAJE
	prompt = "*>>"
	def __init__(self):
		"""Constructor de la clase"""
		super().__init__()
		self.editor = e.Editor()

	def do_cargar(self,file):
		"""Carga la cancion desde el archivo.\n
		Reemplaza la cancion en edicion actual si es que la hay.\n
			-> file (str)"""
		self.editor = a.Almacenamiento(e.Editor()).cargar(file+".plp")

	def do_guardar(self,file):
		"""Guarda la cancion.\n
			-> file (str)"""
		a.Almacenamiento(self.editor).guardar(file+".plp")

	def do_avanzar(self,x=None):
		"""Avanza a la siguiente marca de tiempo.Si no hay mas marcas \n
		hacia adelante, no hace nada."""
		self.editor.avanzar(1)
		print("Marca: ",self.editor.index)

	def do_retroceder(self,x = None):
		"""Retrocede a la anterior marca de tiempo.Si no hay mas marcas\n
		hacia atras, no hace nada."""
		self.editor.retroceder(1)
		print("Marca: ",self.editor.index)

	def do_avanzarm (self, n):
		"""Avanza N marcas de tiempo hacia adelante. Si no hay mas mar\n
		cas hacia adelante, no hace nada."""
		n=validar_parametro(n) 
		if n:
			self.editor.avanzar(n)
			print("Marca: ",self.editor.index)

	def do_retrocederm (self, n):
		"""Retrocede N marcas de tiempo hacia atras. Si no hay mas mar\n
		cas hacia atras, no hace nada."""
		n=validar_parametro(n) 
		if n:
			self.editor.retroceder(n)
			print("Marca: ",self.editor.index)

	def do_trackadd (self, parametros):
		"""Agrega un track con el sonido indicado.\n
			->parametro(str)"""
		lista_p = parametros.split(" ")
		if len(lista_p)== 3:
			funcion, frecuencia, volumen= lista_p[0], lista_p[1], lista_p[2]
		else:
			funcion, frecuencia = lista_p[0], lista_p[1]
			volumen = 100
		frecuencia = validar_parametro(frecuencia)
		volumen = validar_parametro(volumen)
		if funcion in self.editor.sound:
			self.editor.tracks.append((funcion, frecuencia, volumen))
			return
		print("La funcion ingresada no es valida")

	def do_trackdel(self, posicion=None):
		"""Elimina un track por numero.Si no se especifica uno elimina\n
		el ultimo tarck.\n
			-> posicion(str)"""		
		if posicion:
			posicion=validar_parametro(posicion)
			if posicion is not None:
				self.editor.tracks.pop(posicion)
				print("Marca: ",self.editor.index)
		else:
			self.editor.tracks.pop(len(self.editor.tracks) - 1)
			
	def do_markadd(self, duration):
		"""Agrega una marca de tiempo de la duracion establecida.\n
		Originalmente todos los tracks arrancan como deshabilitados.\n
		Siempre que se agrega una marca el cursor vuelve al inicio."""
		duration = validar_parametro(duration) 
		if duration:
			self.editor.timeline.append( _Mark(duration/100))
			self.editor.cursor = self.editor.timeline.prim

	def do_markaddnext(self, duration):
		"""Igual que MARKADD pero la inserta luego de la marca en la \n
		cual esta actualmente el cursor."""
		duration = validar_parametro(duration) 
		if duration:
			self.editor.timeline.insert(self.editor.index+1,_Mark(duration/100))

	def do_markaddprev(self,duration):
		"""Igual que MARKADD pero la inserta antes de la marca en la \n
		cual esta actualmente el cursor."""
		duration = validar_parametro(duration) 
		if duration:
			self.editor.timeline.insert(self.editor.index,_Mark(duration/100))

	def do_trackon(self, indice):
		"""Habilita al track durante la marca de tiempo en la cual \n
		esta parada el cursor."""
		indice = validar_parametro(indice,len(self.editor.tracks)) 
		if indice is not None:
			self.editor.cursor.dato.tracks[self.editor.tracks[indice]] = "#"

	def do_trackoff(self, indice):
		"""Operacion inversa del TRACKON."""
		duration = validar_parametro(indice,len(self.editor.tracks)) 
		if duration is not None:
			self.editor.cursor.dato.tracks.pop(self.editor.tracks[indice])

	def do_play(self, x = None):
		"""Reproduce la marca en la que se encuentra el cursor actual\n
		mente."""
		r.Reproductor(self.editor).play(self.editor.timeline.len)

	def do_playall(self, x = None):
		"""Reproduce la cancion completa desde el inicio.""" 
		cursor_aux = self.editor.cursor
		self.editor.cursor = self.editor.timeline.prim
		r.Reproductor(self.editor).play(self.editor.timeline.len)
		self.editor.cursor = cursor_aux

	def do_playmarks (self, n):
		"""Reproduce las proximas N marcas desde la posicion actual del\n
		 cursor."""
		n = validar_parametro(n)
		if n:
			r.Reproductor(self.editor).play(n)
		
	def do_playsecond(self, n):
		"""Reproduce los proximos N segundos desde la posicion actual \n
		del cursor. Si alguna marca dura mas del tiempo restante, la \n
		reproduccion se corta antes."""
		n = validar_parametro(n)
		if n:
			r.Reproductor(self.editor)(self.editor.timeline.len,n)

	def do_imprimir(self, x = None):
		"""Imprime la timeline que se tiene hasta el momento"""
		for (funcion, frecuencia, volumen) in self.editor.tracks:
			print("Funcion: {} Frecuencia: {} Volumen: {}".format(funcion, frecuencia, volumen))
		cont = 0
		for mark in self.editor.timeline:
			cadena = "["+str(mark.duracion)+"]: "
			for track in self.editor.tracks:
				cadena += mark.tracks.get(track,".")
			if self.editor.index == cont:
				cadena += "<-"	#Señala el cursor
			cont += 1
			print(cadena)
	def do_salir(self, x = None):
		"""Sale del programa"""
		print("Hasta luego")
		exit()