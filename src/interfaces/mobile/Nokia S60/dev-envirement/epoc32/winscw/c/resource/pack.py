# Portions Copyright (c) 2005 Nokia Corporation 
class BuggyFile(IOError): pass

__pkgs = {}
__provides = {}

def parsefield(pkg, field):
	if not pkg.has_key(field):
	#	print field, "not found"
		return {}
	compact = pkg[field].replace(' ', '')
	entries = [x.strip() for x in compact.split(',')]
#	print entries
	dict = {}
	for x in entries:
		if x.find('|') != -1:
		#	print x
			continue	# For now, skip multiple choice ones
		l = x.split('(', 1)
		if (len(l) > 1):
			dict[l[0]] = l[1].replace(')','',1)
		else:
			dict[l[0]] = None
	return dict

def dft(x, rule, depth=0):
	if __pkgs.has_key(x):
		pkg = __pkgs[x]
	elif __provides.has_key(x):
		print "  "*depth + "(" + x + ")"
		for newx in __provides[x]:
			dft(newx, rule, depth)
		return
	else:
		print x, "not found"
		return None
	pkg['visited'] = True
	f = parsefield(pkg, rule)
	for entry, extra in f.items():
		if __provides.has_key(entry):
			flurppa = __pkgs[__provides[entry][0]]
		else:
			flurppa = __pkgs[entry]
		print ' '*2*depth + '+-' + entry + \
			' (' + (extra or '') + ')'
		if not flurppa.has_key('visited'):
			dft(entry, rule, depth+1)

def parse(x):
	for tmp in x.split('\n\n'):
		if tmp == '': continue
		fields = {}
		context = ''
		for line in tmp.splitlines():
		#	print 'DEBUG:', line
			if line[0] != ' ':
				context = line.split(': ')[0]
			#	print 'New context:', context
				fields[context] = ''.join(line.split(': ')[1:])
			else:
				fields[context] += '\n' + line[1:]
		if 'Name' not in fields.keys():
			print fields
			raise BuggyFile, "Buggy File"
		__pkgs[fields['Name']] = fields
		if 'Provides' in fields.keys():
			for p in fields['Provides'].split(','):
				if not __provides.has_key(p.strip()):
					__provides[p.strip()] = []
				__provides[p.strip()].append(fields['Name'])
			#	print p.strip(), '=', __provides[p.strip()]
	return __pkgs

if __name__ == '__main__':
	pkgs = parse(file('Packages').read())
	print pkgs['exim']
	#dft('exim', 'Recommends')
	dft('roxen-doc', 'Depends')

