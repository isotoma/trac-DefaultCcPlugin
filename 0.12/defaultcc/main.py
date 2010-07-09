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

from trac.ticket.api import ITicketChangeListener
from trac.env import IEnvironmentSetupParticipant
from trac.db import Table, Column, Index
from trac.db import DatabaseManager

from defaultcc.model import DefaultCC

class TicketDefaultCC(Component):
    """Automatically adds a default CC list when new tickets are created.

    Tickets are modified right after their creation to add the field's
    default CC list to the ticket CC list.
    """

    implements(IEnvironmentSetupParticipant, ITicketChangeListener)

    # IEnvironmentSetupParticipant

    SCHEMA = [
        Table('default_cc', key=['name', 'field'])[
            Column('name'),
            Column('field'),
            Column('cc'),
            Index(['name', 'field']),
            ]
        ]

    def environment_created(self):
        self._upgrade_db(self.env.get_db_cnx())

    def environment_needs_upgrade(self, db):
        cursor = db.cursor()
        try:
            cursor.execute("select count(*) from default_cc")
            cursor.fetchone()
            return False
        except:
            db.rollback()
            return True

    def upgrade_environment(self, db):
        self._upgrade_db(db)

    def _upgrade_db(self, db):
        try:
            db_backend, _ = DatabaseManager(self.env)._get_connector()
            cursor = db.cursor()
            for table in self.SCHEMA:
                for stmt in db_backend.to_sql(table):
                    self.log.debug(stmt)
                    cursor.execute(stmt)
                    db.commit()
        except Exception, e:
            db.rollback()
            self.log.error(e, exc_info=True)
            raise TracError(str(e))

    # ITicketChangeListener

    def ticket_created(self, ticket):
        default_cc = DefaultCC(self.env, ticket=ticket).cc

        if not default_cc:
            return

        if ticket['cc']:
            default_cc.append(ticket['cc'])

        default_cc = list(set(default_cc))

        ticket['cc'] = ', '.join(default_cc)
        ticket.save_changes('DefaultCC Plugin', '')

    def ticket_changed(self, ticket, comment, author, old_values):
        return

    def ticket_deleted(self, ticket):
        return

