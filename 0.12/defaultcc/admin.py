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

from trac.web.api import IRequestFilter, ITemplateStreamFilter

from genshi.builder import tag
from genshi.filters import Transformer

from defaultcc.model import DefaultCC

class DefaultCCAdmin(Component):
    """Allows to setup a default CC list per component through the component
    admin UI.
    """
    implements(ITemplateStreamFilter, IRequestFilter)

    # TODO: Get a nicer way of finding this out, the panels these are
    # associated with inherit directly from TicketAdminPanel
    # All the other ticket field panels in the Ticket system admin ui
    # inherit from AbstractEnumAdminPanel. Annoyingly, the url is
    # pluralised for these and not the abstractenums, so we have to do this
    # funky bit of manhandling to identify which field we're editing
    _non_abstract_enums = ('component', 'milestone', 'version',)

    def _get_field_name(self, req_args):
        field_name = req_args.get('panel_id', self._non_abstract_enums[0])
        if field_name:
            if field_name.rstrip('s') in self._non_abstract_enums:
                field_name = field_name.rstrip('s')
        return field_name

    # IRequestFilter methods
    def post_process_request(self, req, template, data, content_type):
        return template, data, content_type

    def pre_process_request(self, req, handler):

        field_name = self._get_field_name(req.args)

        if 'TICKET_ADMIN' in req.perm and req.method == 'POST' and \
           req.path_info.startswith('/admin/ticket/') and field_name:

            cc = DefaultCC(self.env, field=field_name)
            if req.args.get('save'):
                cc.delete(req.args.get('old_name'))
                cc.insert(req.args.get('name'), req.args.get('defaultcc'))
            elif req.args.get('remove'):
                if req.args.get('sel'):
                    if isinstance(req.args.get('sel'), basestring):
                        cc.delete(req.args.get('sel'))
                    else:
                        for name in req.args.get('sel'):
                            cc.delete(name)

        return handler

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):

        field_name = self._get_field_name(req.args)

        if 'TICKET_ADMIN' in req.perm and field_name and \
           req.path_info.startswith('/admin/ticket'):

            if field_name in self._non_abstract_enums:
                field_objects = data.get(field_name + 's')
            else:
                field_objects = data.get('enums')

            default_ccs = DefaultCC.select(self.env, field_name)

            if field_objects:
                # list of field objects

                stream = stream | Transformer(
                    '//table[@class="listing"]/thead/tr').append(
                        tag.th('CC'))

                if field_name == 'component':
                    transformer = Transformer('//table[@id="complist"]/tbody')
                    default_comp = self.config.get(
                        'ticket', 'default_component')

                for idx, field_object in enumerate(field_objects):

                    # Milestone object can be a tuple :/
                    try:
                        field_object_name = field_object.name
                    except AttributeError:
                        field_object_name = field_object[0].name

                    if field_object_name in default_ccs:
                        default_cc = default_ccs[field_object_name]
                    else:
                        default_cc = ''

                    # Annoyingly, we can't just append to the row if the
                    # collection is components, it appears to blat it for
                    # rendering later so you end up with no rows
                    # This may be due to the collection being a generator,
                    # but then again, who knows?
                    if field_name == 'component':

                        if default_comp == field_object_name:
                            default_tag = tag.input(
                                type='radio', name='default',
                                value=field_object_name, checked='checked')
                        else:
                            default_tag = tag.input(
                                type='radio', name='default',
                                value=field_object_name)

                        transformer = transformer.append(
                            tag.tr(
                                tag.td(
                                    tag.input(type='checkbox', name='sel',
                                              value=field_object_name),
                                    class_='sel'),
                                tag.td(
                                    tag.a(field_object_name,
                                          href=req.href.admin(
                                              'ticket', 'components') + '/' + \
                                          field_object_name),
                                    class_='name'),
                                tag.td(field_object.owner, class_='owner'),
                                tag.td(default_tag, class_='default'),
                                tag.td(default_cc, class_='defaultcc')
                            )
                        )

                    else:
                        stream = stream | Transformer(
                            '//table[@class="listing"]/tbody/tr[%s]' % (idx+1,)
                            ).append(tag.td(default_cc, class_='defaultcc'))

                if field_name == 'component':
                    return stream | transformer

            else:
                # edit field object
                if field_name in self._non_abstract_enums:
                    field_object = data.get(field_name)
                else:
                    field_object = data.get('enum')

                if field_object:

                    # Milestone object can be a tuple :/
                    try:
                        field_object_name = field_object.name
                    except AttributeError:
                        field_object_name = field_object[0]

                    if field_object_name in default_ccs:
                        default_cc = default_ccs[field_object_name]
                    else:
                        default_cc = ''

                    transformer = Transformer(
                        '//form[@class="mod"]/fieldset/div[@class="buttons"]')
                    transformer = transformer.before(
                        tag.div(tag.label("Default CC:"), tag.br(),
                                tag.input(type="text", name="defaultcc",
                                          value=default_cc),
                                class_="field")
                        ).before(tag.input(type='hidden', name='old_name',
                                           value=field_object_name))

                    return stream | transformer

        return stream
