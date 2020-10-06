# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, 2019, 2020 Esteban J. G. Gabancho.
#
# oarepo-s3 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""API tests."""

from __future__ import absolute_import, print_function

from uuid import UUID

from flask import request
from werkzeug.datastructures import ImmutableMultiDict

from oarepo_s3.api import multipart_uploader


def test_multipart_uploader(app, record):
    """Test multipart uploader."""
    fsize = 1024 * 1024 * 512
    files = record.files
    request.args = ImmutableMultiDict({'size': fsize})

    def _resolver(name, **kwargs):
        return 'http://localhost/records/1/{}'.format(name)

    res = multipart_uploader(record=record, key='test', files=files,
                             pid=None, request=None, resolver=_resolver)
    assert res is not None
    assert callable(res)

    file_rec = files['test']
    file_rec['testparam'] = 'test'

    response = res()
    assert response['testparam'] == 'test'
    assert response.get('multipart_upload', None) is not None
    assert response['multipart_upload']['complete_url'] == _resolver('{0}_upload_complete')
    assert response['multipart_upload']['abort_url'] == _resolver('{0}_upload_abort')

    multi = response['multipart_upload']
    assert isinstance(response, dict)
    assert multi['bucket'] == 'test_invenio_s3'
    assert multi['num_chunks'] == 33
    assert multi['chunk_size'] == 16777216
    assert len(multi['parts_url']) == 33
    assert isinstance(multi['upload_id'], UUID)

    assert file_rec.get('multipart_upload', None) is not None
