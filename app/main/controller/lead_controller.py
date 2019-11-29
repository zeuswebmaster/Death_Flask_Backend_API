from flask import request, current_app
from flask_restplus import Resource
from app.main.model.client import ClientType
from app.main.model.credit_report_account import CreditReportData
from app.main.service.client_service import get_all_clients, save_new_client, get_client
from app.main.service.credit_report_account_service import save_changes
from app.main.service.debt_service import get_report_data, check_existing_scrape_task
from ..util.dto import LeadDto, CandidateDto

api = LeadDto.api
_lead = LeadDto.lead
_credit_report_data = CandidateDto.credit_report_data

LEAD = ClientType.lead


@api.route('/')
class LeadList(Resource):
    @api.doc('list_of_clients')
    @api.marshal_list_with(_lead, envelope='data')
    def get(self):
        """ List all clients """
        clients = get_all_clients(client_type=LEAD)
        return clients

    @api.response(201, 'Client successfully created')
    @api.doc('create new client')
    @api.expect(_lead, validate=True)
    def post(self):
        """ Creates new Client """
        data = request.json
        return save_new_client(data=data, client_type=LEAD)


@api.route('/<public_id>')
@api.param('public_id', 'The Client Identifier')
@api.response(404, 'Client not found')
class Lead(Resource):
    @api.doc('get client')
    @api.marshal_with(_lead)
    def get(self, public_id):
        """ Get client with provided identifier"""
        client = get_client(public_id, client_type=LEAD)
        if not client:
            api.abort(404)
        else:
            return client


@api.route('/<public_id>/credit-report/debts')
@api.param('public_id', 'The client Identifier')
class CreditReportDebts(Resource):
    @api.doc('fetch credit report data')
    def put(self, public_id):
        """ Fetch Credit Report Data"""
        try:
            client, error_response = _handle_get_client(public_id)
            if not client:
                return error_response
            account, error_response = _handle_get_credit_report(client, public_id)
            if not account:
                return error_response
            exists, error_response = check_existing_scrape_task(account)
            if exists:
                return error_response

            task = CreditReportData().launch_spider(
                account.id,
                account.email,
                current_app.cipher.decrypt(
                    account.password).decode()
            )

            save_changes()

            resp = {
                'messsage': 'Spider queued',
                'task_id': task.id
            }
            return resp, 200
        except Exception as e:
            response_object = {
                'success': False,
                'message': str(e)
            }
            return response_object, 500

    @api.doc('view credit report data')
    @api.marshal_list_with(_credit_report_data, envelope='data')
    def get(self, public_id):
        """View Credit Report Data"""
        client, error_response = _handle_get_client(public_id)
        if not client:
            api.abort(404, **error_response)
        data = get_report_data(client.credit_report_account)
        return data, 200


def _handle_get_client(public_id):
    client = get_client(public_id, client_type=LEAD)
    if not client:
        response_object = {
            'success': False,
            'message': 'Client does not exist'
        }
        return None, response_object
    else:
        return client, None


def _handle_get_credit_report(client, public_id):
    account = client.credit_report_account
    # return account, None
    if not account or account.public_id != public_id:
        response_object = {
            'success': False,
            'message': 'Credit Report Account does not exist'
        }
        return None, (response_object, 404)
    else:
        return account, None
