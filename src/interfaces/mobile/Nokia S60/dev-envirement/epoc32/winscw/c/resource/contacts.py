#
# contacts.py
#
# Copyright (c) 2006-2008 Nokia Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import _contacts
def revdict(d):
    return dict([(d[k],k) for k in d.keys()])  
    
#This dictionary is created by calling create_api_mappings()  from contactsmodule.cpp
_api_mappings = {((268440333,), 268451878): (13, 0), ((268440334, 268451441, 268450266), 268451882): (6, 2), ((268441486, 268450267), 268451872): (9, 1), ((268455417,), 268455407): (29, 0), ((268455412, 268450267), 268455402): (23, 1), ((268440332, 268450267), 268451869): (25, 1), ((270551984, 270553033), 270553033): (38, 0), ((268455415,), 268455405): (28, 0), ((268455414,), 268455404): (27, 0), ((268440334, 268451441), 268451882): (6, 0), ((270551984, 270553034, 268450266), 270551985): (36, 2), ((270522711,), 270522807): (31, 0), ((268440444,), 268451886): (2, 0), ((268440334, 268450269, 268450266), 268451882): (5, 2), ((268451893, 268450267), 268451885): (11, 1), ((270551984, 270553034), 270551985): (36, 0), ((268451868,), 268451877): (17, 0), ((268441489, 268450270, 268450266), 268451882): (7, 2), ((268455413, 268450267), 268455403): (24, 1), ((268441486, 268450266), 268451872): (9, 2), ((268473240,), 268451884): (12, 0), ((268455415, 268450266), 268455405): (28, 2), ((270487538,), 268451890): (35, 0), ((270551984, 270553034, 268450267), 270553034): (36, 1), ((268455416,), 268455406): (26, 0), ((268455417, 268450267), 268455407): (29, 1), ((268455416, 268450267), 268455406): (26, 1), ((270551984, 270553034), 270553034): (36, 0), ((268441483,), 268451886): (49, 0), ((268451893,), 268451885): (11, 0), ((270551984, 270553032), 270553032): (37, 0), ((268455413,), 268455403): (24, 0), ((268440332, 268450266), 268451869): (25, 2), ((268440332, 268450267), 268451874): (10, 1), ((268440334, 268450265, 268450266), 268451882): (32, 2), ((268461336,), 268451890): (15, 0), ((270551984, 270551985), 270551985): (39, 0), ((268441489, 268450270), 268451882): (7, 0), ((268459473,), 268451890): (18, 0), ((268451892,), 268451871): (16, 0), ((268440334, 268451441, 268450267), 268451882): (6, 1), ((268455412, 268450266), 268455402): (23, 2), ((268440332,), 268451874): (10, 0), ((268441484,), 268451886): (48, 0), ((268455415, 268450267), 268455405): (28, 1), ((270551984, 270553032), 270551985): (37, 0), ((268441486,), 268451872): (9, 0), ((268455414, 268450266), 268455404): (27, 2), ((270551984, 270553034, 268450267), 270551985): (36, 1), ((268459473,), 268451879): (19, 0), ((268440334, 268451442), 268451882): (8, 0), ((268440445,), 268451886): (1, 0), ((268451893, 268450266), 268451885): (11, 2), ((268455413, 268450266), 268455403): (24, 2), ((268440334, 268450269, 268450267), 268451882): (4, 1), ((268455417, 268450266), 268455407): (29, 2), ((268441489, 268450270, 268450267), 268451882): (7, 1), ((268440334, 268450269), 268451882): (3, 0), ((268461335,), 268451890): (22, 0), ((268440334, 268450265), 268451882): (32, 0), ((268455416, 268450266), 268455406): (26, 2), ((270551984, 270553034, 268450266), 270553034): (36, 2), ((268455414, 268450267), 268455404): (27, 1), ((270551984, 270553033), 270551985): (38, 0), ((268440332, 268450266), 268451874): (10, 2), ((268455412,), 268455402): (23, 0), ((268440332,), 268451869): (25, 0), ((268440334, 268450265, 268450267), 268451882): (32, 1)}

_api_mappings_reverse_map = revdict(_api_mappings)
  
fieldtype_names=["none",
                 "last_name",
                 "first_name",
                 "phone_number_general",
                 #"phone_number_home",  
                 #"phone_number_work",
                 "phone_number_mobile",
                 "fax_number",
                 "pager_number",
                 "email_address",
                 "postal_address",
                 "url",
                 "job_title",
                 "company_name",
#                 "company_address",    # same as postal_address
                 "dtmf_string",
                 "date",
                 "note",
                 "po_box", 
                 "extended_address", 
                 "street_address",
                 "postal_code",
                 "city", 
                 "state", 
                 "country",
                 "wvid", 
                 "prefix",
                 "suffix",
                 "job_title",
                 "second_name",
                 "voip",
                 "push_to_talk",
                 "share_view",
                 "sip_id"] 
                 
fieldtypemap=dict([(k,getattr(_contacts,k)) for k in fieldtype_names])

unknown_field = 'unknown'

fieldtypemap.update({'video_number': 32,
                     'picture': 0x12,
                     'thumbnail_image': 0x13,
                     'voice_tag': 0x14,
                     'speed_dial': 0x15,
                     'personal_ringtone': 0x16,
                     'second_name': 0x1f,
                     'last_name_reading': 0x21,
                     'first_name_reading': 0x22,
                     'locationid_indication': 0x23,
                     unknown_field:-1})
                         
fieldtypemap['mobile_number']=fieldtypemap['phone_number_mobile']
del fieldtypemap['phone_number_mobile']
fieldtypemap['phone_number']=fieldtypemap['phone_number_general']
del fieldtypemap['phone_number_general']
fieldtypereversemap=revdict(fieldtypemap)

unknown_location = 'unknown'

locationmap={None: _contacts.location_none,
             'none': _contacts.location_none,
             'home': _contacts.location_home,
             'work': _contacts.location_work,
             unknown_location:-1}
locationreversemap=revdict(locationmap)
locationreversemap[_contacts.location_none]='none'

_phonenumber_location_map={
    None: _contacts.phone_number_general,
    'none': _contacts.phone_number_general,
    'home': _contacts.phone_number_home,
    'work': _contacts.phone_number_work
    }
_phonenumber_location_reversemap=revdict(_phonenumber_location_map)

storagetypemap={"text":_contacts.storage_type_text,
                "binary":_contacts.storage_type_store,
                "item_id":_contacts.storage_type_contact_item_id,
                "datetime":_contacts.storage_type_datetime}
_storagetypereversemap=revdict(storagetypemap)

def pb_values_from_py_type_and_location(type,location=None):       
    if type=='phone_number':
        return (_phonenumber_location_map[location],locationmap[location])
    return (fieldtypemap[type],locationmap[location])

class ContactsDb(object):
    def __init__(self,dbfile=None,mode=None):
        if dbfile is None:
            self._db=_contacts.open()
        else:
            dbfile = unicode(dbfile)
            if (len(dbfile)<2) or dbfile[1]!=':':
                dbfile = u"c:" + dbfile
            if dbfile.find("\\") >= 0 or dbfile.find('/')>=0:
                raise ValueError("database name cannot have path")
            if mode is None:
                self._db=_contacts.open(dbfile)
            else:
                self._db=_contacts.open(dbfile,mode)
                if mode=='n':
                    for id in self._db:
                        del self._db[id]
        self._have_field_types = 0
        # create several lists and dictionaries to speed up the field type data handling.
        data = self._db.field_types()
        self._raw_field_types= data[0]    # list of id values of each template field [[new_id_1, .., new_id_n], ..] 
        self._vcard_mappings = data[1]    # vcard mappings for each template field [mapping_1, ..]
        self._simple_field_types = []     # list of self._raw_field_types[index][0] for all values of index.
        self._field_types=[]              # [{"name":"field_default_label_1", "storagetype":"text", "type":"last_name", "location":"none"}, ..]
        self._template_field_schema = {}  # {template_field_index:{"name":"field_default_label_1", "storagetype":"text", "type":"last_name", "location":"none"}..}
        self._schema_index_map = {}       # ((new_id_1, .., new_id_n), vcard_mapping):schema_index_1, ..) 
        self._nr_of_field_types = len(self._raw_field_types)
        for index in range(self._nr_of_field_types):
             self._schema_index_map[(tuple(self._raw_field_types[index]), self._vcard_mappings[index])]=index
             self._simple_field_types.append(self._raw_field_types[index][0])   
    def _field_type_pb_to_symbian(self,field_type,location):
        key = ()
        if (location is None) or (location == locationmap['none']) or (location == locationmap[unknown_location]):
            key = (field_type,locationmap['none'])
        else:
            key = (field_type,location)   
        if _api_mappings_reverse_map.has_key(key):
            return _api_mappings_reverse_map[key]      
        raise TypeError("field type " + str(key) + " was not recognized. _api_mappings update needed?")            
    def _field_type_symbian_to_pb(self,new_field_type,vcard_mapping,storage_type='text'):
        key = (tuple(new_field_type),vcard_mapping)       
        if _api_mappings.has_key(key):
            if _api_mappings[key][0] == _contacts.phone_number_home: 
                return (fieldtypemap['phone_number'],locationmap['home'])
            if _api_mappings[key][0] == _contacts.phone_number_work:
                return (fieldtypemap['phone_number'],locationmap['work'])
            return _api_mappings[key]                
        import warnings
        warnings.warn("new fieldtype " + str(key) + " not recognized. _api_mappings update needed?", RuntimeWarning)    
        return (fieldtypemap[unknown_field],locationmap[None])                                   
    def _field_schema(self,schemaid):
        schema=self._db.field_type_info(schemaid)
        schema['storagetype']=_storagetypereversemap[schema['storagetype']]
        old_field_type = self._field_type_symbian_to_pb(self._raw_field_types[schemaid],schema['vcard_mapping'],schema['storagetype'])
        del schema['vcard_mapping']
        schema['location']=locationreversemap[old_field_type[1]]
        if fieldtypereversemap.has_key(old_field_type[0]):
            schema['type']=fieldtypereversemap[old_field_type[0]]
        else:
            schema['type']=unknown_field
        return schema       
    def field_types(self):
        if self._have_field_types==0:
            for index in range(self._nr_of_field_types):
                self._field_types.append(self._field_schema(index))
            self._have_field_types=1          
        return list(self._field_types)    
    def _search_field_uids(self,vcard_match,field_uids):      
        #go through match list and check
        longest_match=0
        found_index=-1
        for item in vcard_match:
            match_count=0
            for template_uid in self._raw_field_types[item]:
                if template_uid in field_uids:
                    match_count+=1
                if match_count==len(field_uids):break  
            if longest_match<match_count: 
                longest_match=match_count
                found_index=item
                if longest_match==len(field_uids):break
        if found_index>=0:                
            return found_index
        else: return None    
    def _search_vcard_mapping(self,vcard_id):
        vcard_match=[]
        for i in xrange (len(self._vcard_mappings)):
            if self._vcard_mappings[i]==vcard_id:
              vcard_match.append(i)
        return vcard_match 
    def _determine_field_type(self,storage_type,field_uids,vcard_id,find_uids=None):
        key = (tuple(field_uids),vcard_id)
        if self._schema_index_map.has_key(key):
            return self._schema_index_map[key]
        #try to match to ids in find_uids list   
        if find_uids!=None:
            matching=1
            for uid in field_uids:
              if uid not in find_uids: 
                  matching=0
                  break
            if matching==1:
                return self._raw_field_types.index(find_uids)      
        vcard_match=self._search_vcard_mapping(vcard_id)
        if len(vcard_match)>0:
            found_index=self._search_field_uids(vcard_match,field_uids)
            if found_index==-1:
                #really broken field, map to one of templates with same vcard_id
                return vcard_match[0]
            else:
                return found_index
        else:
            return None       
    def __iter__(self):
        return iter(self._db)
    def __getitem__(self,key):
        return ContactsDb.Contact(self._db.get_entry(key),self)
    def __delitem__(self,key):
        self._db.delete_entry(key)
    def __len__(self):
        return self._db.entry_count()
    def add_contact(self):
        return ContactsDb.Contact(self._db.create_entry(),self,locked='as_new_contact')
    def keys(self):
        return list(self._db)
    def values(self):
        return [self[k] for k in self]
    def items(self):
        return [(k,self[k]) for k in self]
    def _build_vcard_flags(self,include_x=0,ett_format=0,exclude_uid=0,decrease_access_count=0,increase_access_count=0,import_single_contact=0):
        vcard_flags=0
        if include_x:
            vcard_flags|=_contacts.vcard_include_x
        if ett_format:
            vcard_flags|=_contacts.vcard_ett_format
        if exclude_uid:
            vcard_flags|=_contacts.vcard_exclude_uid
        if decrease_access_count:
            vcard_flags|=_contacts.vcard_dec_access_count
        if increase_access_count:
            vcard_flags|=_contacts.vcard_inc_access_count
        if import_single_contact:
            vcard_flags|=_contacts.vcard_import_single_contact
        return vcard_flags
    def import_vcards(self,vcards,include_x=1,ett_format=1,import_single_contact=0):
        vcard_flags=self._build_vcard_flags(include_x,ett_format,0,0,0,import_single_contact)
        return [self[x] for x in self._db.import_vcards(unicode(vcards),vcard_flags)]
    def export_vcards(self,vcard_ids,include_x=1,ett_format=1,exclude_uid=0):
        vcard_flags=self._build_vcard_flags(include_x,ett_format,exclude_uid)
        return self._db.export_vcards(tuple(vcard_ids),vcard_flags)
    def find(self,searchterm):
        return [self[x] for x in self._db.find(unicode(searchterm),tuple(self._simple_field_types))]
    def compact_required(self): 
        return self._db.compact_recommended()
    def compact(self):
        return self._db.compact()
    class ContactsIterator(object):
        def __init__(self,db,_iter):
            self.db=db
            self._iter=_iter
        def next(self):
            return self.db[self._iter.next()]
        def __iter__(self):
            return self
    class Contact(object):
        def __init__(self,_contact,db,locked=0):
            self._contact=_contact
            self.db=db
            self._locked=locked
        def _data(self,key):
            return self._contact.entry_data()[key]
        id=property(lambda self:self._data('uniqueid'))
        last_modified=property(lambda self:self._data('lastmodified'))
        def _get_title(self):
            first_name_indexes = self._contact.find_field_indexes(_contacts.given_name_value)
            last_name_indexes = self._contact.find_field_indexes(_contacts.family_name_value)
            title_str = u""
            for index in last_name_indexes:
                title_str += self._contact.get_field(index)['value'] + u" "
            for index in first_name_indexes:
                title_str += self._contact.get_field(index)['value'] + u" "
            if len(title_str)>0:
                title_str = title_str[:len(title_str)-1]
            return title_str  
        title=property(_get_title)
        def add_field(self,type,value=None,location=None,label=None): 
            #fetch list with nokia phonebook values form python-side  call.    pb_type_and_location= (type, location)
            fieldtype = pb_values_from_py_type_and_location(type,location)
            type=fieldtype[0]
            location=fieldtype[1]
            #do the mapping from nokia phonebook API to symbian API field UID
            #symb_key = (   (UID1,UID2...UIDx),(vcardID) )
            symb_key=self.db._field_type_pb_to_symbian(type,location)     
            template_ID=self.db._raw_field_types.index(list(symb_key[0]))    
            field_data = self.db._db.field_type_info(template_ID)
            kw={}
            if value is not None:
                if field_data['storagetype'] == _contacts.storage_type_text:
                    kw['value']=unicode(value)
                else:
                    kw['value']=value
            if label is not None: 
                kw['label']=unicode(label)
            if not self._locked:
                self._begin()
            self._contact.add_field(template_ID,**kw)
            if not self._locked:
                self._contact.commit()       
        def __len__(self):
            return self._contact.num_of_fields()
        def __getitem__(self,key):
            if isinstance(key,int):
                if key >= self._contact.num_of_fields():
                    raise IndexError
                return ContactsDb.ContactField(self,key)
            raise TypeError('field indices must be integers')
        def __delitem__(self,index):
            self[index] # Check validity of index
            # NOTE: After this all ContactFields will have incorrect indices!
            if not self._locked:
                self._begin()
            self._contact.remove_field(index)
            if not self._locked:
                self._contact.commit()  
        def _create_search_result(self,new_search_result,old_search_result):
            result=old_search_result
            for new_field in new_search_result:
              exists=0
              for old_field in old_search_result:
                if new_field.index==old_field.index:
                  exists=1
                  break
              if (exists==0):result.append(new_field)  
            return result  
        def find(self,type=None,location=None):
            if type:
                if location is None:
                    result=self.find(type,'none')
                    result_home=self.find(type,'home')
                    result=self._create_search_result(result_home,result)
                    result_work=self.find(type,'work')
                    result=self._create_search_result(result_work,result)        
                    return result             
                if type == 'phone_number':     
                    typecode=_phonenumber_location_map[location]
                else:
                    typecode=fieldtypemap[type]
                new_type=None
                try:
                    new_type = self.db._field_type_pb_to_symbian(typecode,locationmap[location])
                except:
                    return [] # this combination of type and location is not recognized. 
                new_type_ids = list(new_type[0])
                tmp_indices = self._contact.find_field_indexes(new_type[0][0])
                indices = []
                for index in tmp_indices:            
                    field_data = self._contact.get_field(index)
                    if (new_type_ids == field_data['field_ids']) and (new_type[1] == field_data['vcard_mapping']):
                        # exact match
                        indices.append(index)
                        continue
                    schema_index = self.db._determine_field_type(field_data['storagetype'],field_data['field_ids'],field_data['vcard_mapping'],new_type_ids) 
                    if schema_index!=None:
                        if (new_type_ids == self.db._raw_field_types[schema_index]) and (new_type[1] == self.db._vcard_mappings[schema_index]):
                            indices.append(index)      
                fields = []
                for index in indices:
                    field = ContactsDb.ContactField(self,index)
                    fields.append(field)
                return fields        
            else:
                if location is not None: # this is slow, but this should be a rare case
                    return [x for x in self if locationmap[x.location]==locationmap[location]]
                else: # no search terms, return all fields
                    return list(self)
        def keys(self):
            return [x['fieldindex'] for x in self._contact]
        def __str__(self):
            return '<Contact #%d: "%s">'%(self.id,self.title.encode('ascii','replace'))
        __repr__=__str__
        def _set(self,index,value=None,label=None):
            if not self._locked:
                self._begin()
            kw={}
            field_data = self._contact.get_field(index)
            if value is not None:
                if field_data['storagetype'] == _contacts.storage_type_text:
                    kw['value']=unicode(value)
                else:
                    kw['value']=value     
            if label is not None: kw['label']=unicode(label)
            self._contact.modify_field(index,**kw)
            if not self._locked:
                self._contact.commit()            
        def _begin(self):
            try:
                self._contact.begin()
            except SymbianError:
                raise RuntimeError("contact is busy")
        def begin(self):
            if self._locked:
                raise RuntimeError('contact already open')
            self._begin()
            self._locked=1
        def commit(self):
            if not self._locked:
                raise RuntimeError('contact not open')
            self._contact.commit()
            self._locked=0
        def rollback(self):
            if not self._locked:
                raise RuntimeError('contact not open')
            if self._locked == 'as_new_contact':
                # clear the content of new uncommited _contact by creating a new _contact.
                self._contact=self.db._db.add_contact()
            else:
                # clear the content of old committed _contact by fetching the last committed data from the database.
                self._contact.rollback()
            self._locked=0
        def __del__(self):
            if self._locked:
                import warnings
                warnings.warn("contact still locked in destructor", RuntimeWarning)
        def as_vcard(self):
            return self.db.export_vcards((self.id,))
        def _is_group(self):
            return self._contact.is_contact_group() 
        is_group = property(_is_group)
            

    class ContactField(object):
        def __init__(self,contact,index):
            self.contact=contact
            self.index=index
        
        def _get_schema(self):
            field_data = self.contact._contact.get_field(self.index)
            schema_index = self.contact.db._determine_field_type(field_data['storagetype'],field_data['field_ids'],field_data['vcard_mapping'])
            # If contact field is not supported by the device as well as PyS60
            # then schema of type unknown is returned.
            if schema_index is None:
                unfound_schema = {'storagetype': 'unknown',
                                  'type':'unknown',
                                  'name':'unknown',
                                  'location':'unknown'}
                return unfound_schema
            if schema_index not in self.contact.db._template_field_schema.keys():
                found_schema=self.contact.db._field_schema(schema_index)
                self.contact.db._template_field_schema[schema_index]=found_schema
            else:
                found_schema=self.contact.db._template_field_schema[schema_index]
            return found_schema
        schema=property(_get_schema)
        type=property(lambda self:self.schema['type'])
        label=property(lambda self: self.contact._contact.get_field(self.index)['label'],
                       lambda self,x: self.contact._set(self.index,label=x))
        value=property(lambda self: self.contact._contact.get_field(self.index)['value'],
                       lambda self,x: self.contact._set(self.index,value=x))
        location=property(lambda self:self.schema['location'])
        
        def _value_representation(self):
            if isinstance(self.value,unicode):
                return self.value.encode('ascii','replace')
            return self.value
            
        def _label_representation(self):
            if isinstance(self.label,unicode):
                return self.label.encode('ascii','replace')
            return self.label
            
        
        def __str__(self):
            return '<field #%d of %s: type=%s value=%s location=%s label=%s>'%(self.index, 
                                                                               self.contact,
                                                                               self.type,
                                                                               self._value_representation(),
                                                                               self.location,
                                                                               self._label_representation())
        __repr__=__str__
        
        
    # Group handling
    class Groups(object):
        def __init__(self,db):
            self._db=db
        def __getitem__(self, group_id):
            return ContactsDb.Group(group_id,self._db)
        def add_group(self,name=None):     
            grp = ContactsDb.Group(self._db._db.create_contact_group(),self._db)
            if name is not None:
                grp.name=name
            return grp
        def __delitem__(self, group_id):
            if self._db[group_id].is_group == 0:
                raise RuntimeError('not a group')
            del self._db[group_id]
        def __iter__(self):
            return iter(self._db._db.contact_groups())
        def __len__(self):
            return self._db._db.contact_group_count() 
    class Group(object):
        def __init__(self,group_id,db):
            self._group_id=group_id
            self._db=db
        def __iter__(self):
            return iter(self._db._db.contact_group_ids(self._group_id))
        def __getitem__(self,index):
            return self._db._db.contact_group_ids(self._group_id)[index]
        def append(self,contact_id):
            self._db._db.add_contact_to_group(contact_id,self._group_id)
        def __delitem__(self,index):
            self._db._db.remove_contact_from_group(self[index],self._group_id)
        def __len__(self):
            return len(self._db._db.contact_group_ids(self._group_id))
        def _get_id(self):
            return self._group_id
        id=property(_get_id)
        def _set_name(self,newname):
            self._db._db.contact_group_set_label(self._group_id,unicode(newname))
        def _get_name(self):
            return self._db._db.contact_group_label(self._group_id)
        name=property(_get_name,_set_name)
    groups=property(lambda self: ContactsDb.Groups(self))    

def open(dbfile=None,mode=None):
    return ContactsDb(dbfile,mode)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
