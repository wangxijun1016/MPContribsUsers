# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
from mpcontribs.rest.rester import MPContribsRester
from mpcontribs.io.archieml.mpfile import MPFile
from mpcontribs.io.core.components import Table

class CarrierTransportRester(MPContribsRester):
    """CarrierTransport-specific convenience functions to interact with MPContribs REST interface"""
    query = {'project': 'carrier_transport'}
    released = True

    def get_contributions(self, limit=20):

        docs = self.query_contributions(
            projection={'_id': 1, 'identifier': 1, 'content': 1}, limit=limit) # use URL for all data
        if not docs:
            raise Exception('No contributions found for CarrierTransport Explorer!')

        data = []
        columns = ['##'.join(['general', sk]) for sk in ['mp-id', 'cid', 'formula']]
        keys, subkeys = ['<mₑᶜᵒⁿᵈ>', '<S>', '<σ>', '<S²σ>'], ['n', 'p']
        columns += ['##'.join([k, sk]) for k in keys for sk in subkeys]

        for doc in docs:
            mpfile = MPFile.from_contribution(doc)
            mp_id = mpfile.ids[0]
            contrib = mpfile.hdata[mp_id]
            cid_url = self.get_cid_url(doc)
            row = [mp_id, cid_url, contrib['extra_data']['pretty_formula']]
            row += [
                contrib['data'].get(k[1:-1], {}).get(sk, {}).get('<ε>', 'n.a. mₑ')
                for k in keys for sk in subkeys
            ]
            data.append((mp_id, row))

        return Table.from_items(data, orient='index', columns=columns)

    def get_detail_data(self,doping):
        '''
            function to get doping and temperature related to the max values
            and the three eigenvalues of the effective mass tensor
        '''

        dopings = ['n', 'p']
        if doping not in dopings:
            raise Exception('doping has to be n or p!')

        docs = self.query_contributions(projection={'_id': 1, 'identifier': 1, 'content': 1})
        if not docs:
            raise Exception('No contributions found for CarrierTransport Explorer!')

        data = []
        columns = ['mp-id', 'cid', 'formula', u'mₑᶜᵒⁿᵈ', u"Sₘₐₓ", u"σₘₐₓ", u"κₑ₋ₘᵢₙ"]
        for doc in docs:
            mpfile = MPFile.from_contribution(doc)
            mp_id = mpfile.ids[0]
            contrib = mpfile.hdata[mp_id]['data']

            details = {k:[contrib[k][doping]['temperature'],contrib[k][doping]['doping']] for k in columns[4:]}
            data.append((mp_id, details))

        return data
