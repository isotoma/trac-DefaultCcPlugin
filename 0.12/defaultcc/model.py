# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 ERCIM, 2010 Isotoma
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Authors: Jean-Guilhem Rouel <jean-guilhem.rouel@ercim.org>
#          Vivien Lacourba <vivien.lacourba@ercim.org>
#          Ben Miller <ben.miller@isotoma.com>
#

from trac.core import *
from trac.ticket.model import simplify_whitespace
from trac.ticket.api import TicketSystem

class DefaultCC(object):
    """Class representing ticket properties default CC lists
    """
    def __init__(self, env, ticket=None, field=None, db=None):
        self.env = env
        self.field = field
        self.cc = []

        if ticket:

            field_names = DefaultCC.get_field_names(env)

            if not db:
                db = self.env.get_db_cnx()
            cursor = db.cursor()

            sql = "SELECT cc FROM default_cc WHERE "
            args = []

            for name in field_names:
                if isinstance(ticket[name], basestring):
                    sql += "(field=%s AND name=%s) OR "
                    args.append(name)
                    args.append(ticket[name])

            # remove extra OR
            sql = sql[:-4]

            cursor.execute(sql, args)

            for row in cursor:
                self.cc.extend([_cc.strip() for _cc in row[0].split(',')])

    def delete(self, name, db=None):
        if not db:
            db = self.env.get_db_cnx()
            handle_ta = True
        else:
            handle_ta = False

        cursor = db.cursor()
        self.env.log.info('Deleting %s %s\'s default CC' % \
                          (self.field, name,))
        cursor.execute("DELETE FROM default_cc "
            "WHERE name=%s AND field=%s", (name, self.field))

        if handle_ta:
            db.commit()

    def insert(self, name, cc, db=None):

        if not db:
            db = self.env.get_db_cnx()
            handle_ta = True
        else:
            handle_ta = False

        cursor = db.cursor()
        self.env.log.debug("Creating %s %s's default CC" % \
                           (self.field, name,))

        cursor.execute("INSERT INTO default_cc (name, field, cc) "
                       "VALUES (%s, %s, %s)",
                       (name, self.field, cc,))

        if handle_ta:
            db.commit()

    @classmethod
    def select(cls, env, field, name=None, db=None):
        if not db:
            db = env.get_db_cnx()
        cursor = db.cursor()

        if name:
            cursor.execute("SELECT name, cc FROM default_cc "
                           "WHERE name=%s "
                           "AND field=%s "
                           "ORDER BY name", (name, field,))

            return cursor.fetchone()
        else:
            cursor.execute("SELECT name, cc FROM default_cc "
                           "WHERE field=%s "
                           "ORDER BY name", (field,))
            res = {}
            for name, cc in cursor:
                res[name] = cc

            return res

    @classmethod
    def get_field_names(cls, env):
        return [f['name'] for f in TicketSystem(env).get_ticket_fields()]

