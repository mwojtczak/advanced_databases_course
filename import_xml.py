# -*- coding: utf-8 -*-

from lxml import etree
import yaml
from io import StringIO
import psycopg2
from psycopg2.extensions import AsIs
from os.path import expanduser


FILENAME = 'dblp.xml'

PUBLICATION_TYPES = ['article', 'inproceedings', 
	'proceedings', 'book', 'incollection', 'phdthesis', 
	'mastersthesis', 'www']

PUBLICATION_COLUMNS = ['key', 'type', 'booktitle', 'mdate', 
	'volume', 'year', 'journal', 'month', 'school', 'isbn', 
	'chapter', 'cdrom', 'crossref', 'number', 'pages']

POSSIBLE_STRINGS = ['booktitle', 'journal', 'month', 'school', 'isbn', 
	'chapter', 'cdrom', 'crossref',]


PUBLICATION_REFERENCES = ['title', 'publisher', 'editor', 'note', 'series']

PUBLICATION_TABLES = ['author', 'cite', 'url', 'ee']

def parse_file_and_find_root(filename):
	parser = etree.XMLParser(encoding="utf-8", load_dtd=True)
	tree = etree.parse(filename, parser);
	return tree.getroot()


def get_dblp_tag(root):
	while root.tag != 'dblp':
		root = root[0]
	return root

def get_last_id(cursor):
	cursor.execute('SELECT LASTVAL()')
	return cursor.fetchone()[0]


def get_database_connection():
	home = expanduser("~/")
	with open(home + 'data.yaml', "r") as config_file:
		auth = list(yaml.load_all(config_file))[0]
	try:
		conn = psycopg2.connect(**auth)
	except Exception as e:
		return None
	conn.autocommit = True
	conn.set_isolation_level(4)
	return conn


def unknown_attr(root, attr):
	print("unproceeded attr " + attr + " in " + root.tag)


def error_print(tree_name, elem):
	print("Not preformed " + elem.tag + " in subtree " + tree_name)
	print_tree(elem)


def create_record_series(root, connection):
	name = root.text.encode('utf-8', 'ignore')
	href = ""
	for key in root.keys():
		if key == 'href' and not href:
			href = root.get('href').encode('utf-8', 'ignore')
		else:
			print("unproceeded keys in series: " + str(root.keys()))
	for child in root:
		error_print(root.tag, child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO series (name, href) VALUES(%s, %s);", [name, href])
	return get_last_id(cursor)

def create_record_publisher(root, connection):
	publisher = root.text.encode('utf-8', 'ignore')
	href = ""
	if root.keys():
		print("unproceeded keys in publisher: " + str(root.keys()))
	for child in root:
		if child.tag == 'href' and not href:
			href = child.text.encode('utf-8', 'ignore')
		else:
			error_print(root.tag, child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO publisher (publisher, href) VALUES(%s, %s)", [publisher, href]);
	return get_last_id(cursor)

def create_record_editor(root, connection):
	editor = root.text.encode('utf-8', 'ignore')
	aux = ""
	orcid = ""
	if root.keys():
		print("unproceeded keys in editor: " + str(root.keys()))
	for child in root:
		if child.tag == 'aux' and not aux:
			aux = child.text.encode('utf-8', 'ignore')
		elif child.tag == 'orcid' and not orcid:
			orcid = child.text.encode('utf-8', 'ignore')
		else:
			error_print(root.tag, child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO editor (editor, aux, orcid) VALUES(%s, %s, %s)", [editor, aux, orcid]);
	return get_last_id(cursor)


def create_publication_cite(root, connection):
	publication_key = root.getparent().get('key')
	label = root.text.encode('utf-8', 'ignore')
	ref = ""
	for key in root.keys():
		if key == 'label':
			label = root.get('label').encode('utf-8', 'ignore')
		else:
			print("unproceeded key in cite " + key)
	for child in root:
		if child.tag == 'ref' and not ref:
			ref = child.text.encode('utf-8', 'ignore')
		else:
			error_print(root.tag, child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO publication_cite (publication, label, ref) VALUES(%s, %s, %s);", [publication_key, label, ref])


def create_publication_url(root, connection):
	publication_key = root.getparent().get('key')
	url = root.text.encode('utf-8', 'ignore')
	aux = ""
	if root.keys():
		print("unproceeded keys in url: " + str(root.keys()))
	for child in root:
		if child.tag == 'aux' and not aux:
			aux = child.text.encode('utf-8', 'ignore')
		else:
			error_print(root.tag, child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO url (publication, url, aux) VALUES(%s, %s, %s);", [publication_key, url, aux])


def create_publication_ee(root, connection):
	publication_key = root.getparent().get('key')
	ee = root.text.encode('utf-8', 'ignore')
	aux = ""
	if root.keys():
		print("unproceeded keys in ee: " + str(root.keys()))
	for child in root:
		if child.tag == 'aux' and not aux:
			aux = child.text.encode('utf-8', 'ignore')
		else:
			error_print(root.tag, child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO ee (publication, ee, aux) VALUES(%s, %s, %s);", [publication_key, ee, aux])


def create_author_record(root, connection):
	name = root.text.encode('utf-8', 'ignore')
	aux = ""
	bibtex = ""
	orcid = ""
	if root.keys():
		print("unproceeded keys in author: " + str(root.keys()))
	for child in root:
		if child.tag == 'aux' and not aux:
			aux = child.text.encode('utf-8', 'ignore')
		elif child.tag == 'bibtex' and not bibtex:
			bibtex = child.text.encode('utf-8', 'ignore')
		elif child.tag == 'orcid' and not orcid:
			orcid = child.text.encode('utf-8', 'ignore')
		else:
			error_print(root.tag, child)
	
	cursor = connection.cursor()
	cursor.execute("INSERT INTO author (name, aux, bibtex, orcid) VALUES(%s, %s, %s, %s);", [name, aux, bibtex, orcid])
	cursor.execute('SELECT LASTVAL()')
	lastid = cursor.fetchone()[0]
	art_key = root.getparent().get('key')
	cursor.execute("INSERT INTO publication_author (publication, author) VALUES(%s, %s);", [art_key, lastid])


def create_title_record(root, connection):
	title = root.text
	if title:
		title = title.encode('utf-8', 'ignore')
	bibtech = ''
	for key in root.keys():
		if key == 'bibtech':
			bibtech = root.get('bibtech').encode('utf-8', 'ignore')
		else:
			error_print(root.tag + " KEYS: ", child)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO title (title, bibtex) VALUES(%s, %s);", [title, bibtech])
	cursor.execute('SELECT LASTVAL()')
	lastid = cursor.fetchone()[0]
	return lastid


def create_note_record(root, connection):
	label = root.text.encode('utf-8', 'ignore')
	type = ''
	for key in root.keys():
		if key == 'type':
			type = root.get('type').encode('utf-8', 'ignore')
		else:
			error_print(root.tag + " KEYS: ", key)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO note (label, type) VALUES(%s, %s);", [label, type])
	cursor.execute('SELECT LASTVAL()')
	lastid = cursor.fetchone()[0]
	return lastid

def create_reference_record(root, connection):
	if root.tag == 'title':
		return create_title_record(root, connection)
	elif root.tag == 'note':
		return create_note_record(root, connection)
	elif root.tag == 'series':
		return create_record_series(root, connection)
	elif root.tag == 'editor':
		return create_record_editor(root, connection)
	elif root.tag == 'publisher':
		return create_record_publisher(root, connection)
	else:
		print("Unknown tag in xml: " + root.tag)

def create_table_record(root, connection):
	if root.tag == 'author':
		return create_author_record(root, connection)
	elif root.tag == 'cite':
		return create_publication_cite(root, connection)
	elif root.tag == 'ee':
		return create_publication_ee(root, connection)
	elif root.tag == 'url':
		return create_publication_url(root, connection)
	else:
		print("Unknown tag in xml: " + root.tag)

def insert_publication(root, conn):
	if root.tag in PUBLICATION_TYPES:
		data = {}
		data['type'] = root.tag
		data['key'] = root.get('key')
		data['mdate'] = root.get('mdate')
		
		for key in root.keys():
			if key == 'publtype':
				data[key] = root.get(key).encode('utf-8', 'ignore')
			else:
				if key != 'mdate' and key != 'key':
					unknown_attr(root, key)

		for elem in root:
			if elem.tag in PUBLICATION_COLUMNS:
				if elem.tag in POSSIBLE_STRINGS:
					data[elem.tag] = elem.text.encode('utf-8', 'ignore')
			elif elem.tag in PUBLICATION_REFERENCES:
				id = create_reference_record(elem, conn)
				data[elem.tag] = id
			elif elem.tag in PUBLICATION_TABLES:
				create_table_record(elem, conn)
			else:
				error_print(root.tag, elem)
		cursor = conn.cursor()
		columns = data.keys()
		values = [data[column] for column in columns]
		insert_statement = 'insert into publication (%s) values %s'
		cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
	else:
		print("Unknown publication type: " + root.tag)



root = parse_file_and_find_root(FILENAME)
print("file parsed")
root = get_dblp_tag(root)
print("database connected")
conn = get_database_connection()
cursor = conn.cursor()
counter = 0

for child in root:
	insert_publication(child, conn)
	counter += 1
	if counter == 100:
		conn.commit()
		counter = 0
conn.commit()
print("inserting data ended")
cursor.execute("ALTER TABLE publication_cite ADD CONSTRAINT const_cite FOREIGN KEY (publication) REFERENCES publication (key) MATCH FULL;")
cursor.execute("ALTER TABLE url ADD CONSTRAINT const_url FOREIGN KEY (publication) REFERENCES publication (key) MATCH FULL;")
cursor.execute("ALTER TABLE publication_author ADD CONSTRAINT const_author FOREIGN KEY (publication) REFERENCES publication (key) MATCH FULL;")
cursor.execute("ALTER TABLE ee ADD CONSTRAINT const_ee FOREIGN KEY (publication) REFERENCES publication (key) MATCH FULL;")
conn.commit()
conn.close()
print("closing bd connection")

