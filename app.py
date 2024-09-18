from bson import ObjectId
from flask import Flask, request, jsonify, Response, json
from pymongo import MongoClient
# If you guys have trouble importing this send me a message :)
from flask_restx import Api, fields, Resource

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config['RESTX_MASK_SWAGGER'] = False
api = Api(app, version='1.0', title='Job API', description='Python jobs', doc='/swagger',
          default_swagger_filename='Job Operations', default="Job Board", default_label="Python Jobs")

# Connects to db
try:
    client = MongoClient(host='localhost', port=27017)
    client.server_info()
    db = client['projectPrototype']
    collection = db['protoCollection']
except Exception as e:
    print(e)
    print(f"{e} Can't connect to db")

# This is for the docs and to handle validation, so if let's say you try to enter a field that's not supposed to be in
# the mongo collection it will throw a validation error.
job_model = api.model('Job', {
    'title': fields.String(required=True, description='Job title', example="This is a Python dev job"),
    'company': fields.String(required=True, description='Company name', example='The API python devs inc'),
    'location': fields.String(required=True, description='Job location', example='Ottawa'),
})

job_model_response = api.model('JobResponse', {
    '_id': fields.String(description='Id of the job', example='66eb21b2adf5db590529e5fe'),
    'title': fields.String(required=True, description='Job title', example="This is a Python dev job"),
    'company': fields.String(required=True, description='Company name', example='The API python devs inc'),
    'location': fields.String(required=True, description='Job location', example='Ottawa'),
})

delete_model_response = api.model('DeleteResponse', {
    'id': fields.String(description='Id of the job deleted', example='66eb21b2adf5db590529e5fe'),
    'message': fields.String(description='Message of response', example='Job deleted successfully')
})


# posts multiple jobs
@api.route('/insert_jobs', endpoint='insert_jobs')
@api.doc(description='Handles inserting multiple jobs to the database',
         responses={200: "Jobs inserted successfully!", 400: "Error inserting Jobs!"})
class InsertJobs(Resource):
    @api.expect([job_model], validate=True)
    def post(self):
        try:
            data = request.get_json()

            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                result = collection.insert_many(data)
                return Response(
                    response=json.dumps(
                        {"message": "Jobs inserted successfully!", 'inserted_ids': str(result.inserted_ids)}),
                    status=200,
                    mimetype="application/json"
                )
            return Response(
                response=json.dumps(
                    {"message": "Error inserting jobs!"}),
                status=400,
                mimetype="application/json"
            )

        except Exception as ex:
            return jsonify({'error': str(ex)}), 500


# posts 1 job
@api.route('/insert_job', endpoint='insert_job')
@api.doc(description="Handles inserting one job to the database",
         responses={200: "Job posted successfully!", 400: "Data can't be inserted"})
class InsertJob(Resource):
    @api.expect([job_model], validate=True)
    def post(self):
        try:
            data = request.get_json()

            if isinstance(data, dict):
                result = collection.insert_one(data)
                return Response(
                    response=json.dumps(
                        {"message": "Job posted successfully!", 'inserted_id': str(result.inserted_id)}),
                    status=200,
                    mimetype="application/json"
                )
            else:
                return Response(
                    response=json.dumps({"message": "Data can't be inserted"}),
                    status=400,
                    mimetype="application/json"
                )
        except Exception as ex:
            return Response(
                response=json.dumps({"message": f"{ex} Error inserting data"}),
                status=400,
                mimetype="application/json"
            )


# Gets all jobs
@api.route('/get_jobs', endpoint='/get_jobs')
@api.doc(description='Gets all jobs from the database',
         responses={200: "Job posted successfully!", 500: "Get All jobs failed"})
class GetAllJobs(Resource):
    @api.marshal_with(job_model_response, as_list=True)
    def get(self):
        try:
            # if we don't do this it's a cursor not a list
            response = list(collection.find())

            for item in response:
                item["_id"] = str(item["_id"])

            # I started doing it with raw flask, with it we have to make it json.dumps. But since we use marshal_with
            # it already handles it for us.
            # json_response = json.dumps(response)
            return response
        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message": "Get All jobs failed"}),
                status=500,
                mimetype="application/json"
            )


# Gets one job
@api.route('/get_job/<job_id>', endpoint='/get_job')
@api.doc(description='Gets one job from database',
         responses={500: "Get Job failed"})
class GetJob(Resource):
    @api.marshal_with(job_model_response)
    def get(self, job_id):
        try:
            obj_id = ObjectId(job_id)
            response = collection.find_one({"_id": obj_id})

            return response
        except Exception as ex:
            return Response(
                response=json.dumps({f"{ex} message": "Get Job failed"}),
                status=400,
                mimetype="application/json"
            )


# Updates one job
@api.route("/update_job/<job_id>",  endpoint='/update_job')
@api.doc(description='Updates one job from database',
         responses={200: "Job updated successfully", 500: "Can't update job", 404: "Job not found"})
class UpdateJob(Resource):
    @api.expect([job_model], validate=True)
    def patch(self, job_id):
        try:

            data = request.get_json()
            updated_job = {
                "$set": {
                    "title": data.get("title"),
                    "company": data.get("company"),
                    "location": data.get("location")
                }
            }
            response = collection.update_one({"_id": ObjectId(job_id)}, updated_job)
            if response.modified_count > 0:
                return Response(
                    response={json.dumps({"message": "Job updated successfully"})},
                    status="200",
                    mimetype="application/json"
                )
            return Response(
                response={json.dumps({"message": "Job not found"})},
                status="404",
                mimetype="application/json"
            )

        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message:": "Can't update job"}),
                status=500,
                mimetype="application/json"
            )


# deletes one job
@api.route("/delete_job/<job_id>", endpoint='/delete_job')
@api.doc(description='Deletes one job from the database',
         responses={
                    500: "Job can't be deleted",
                    404: "Job not found: job_id"})
class DeleteJob(Resource):
    @api.response(200, "Delete model", delete_model_response)
    def delete(self, job_id):
        try:
            response = collection.delete_one({"_id": ObjectId(job_id)})

            if response.deleted_count > 0:
                return Response(
                    response=json.dumps({"message": "Job deleted successfully", "id": job_id}),
                    status=200,
                    mimetype="application/json"
                )
            return Response(
                response=json.dumps({"message": "Job not found", "id": job_id}),
                status=404,
                mimetype="application/json"
            )
        except Exception as ex:
            print(ex)
            return Response(
                response=json.dumps({"message": "Job can't be deleted"}),
                status=500,
                mimetype="application/json"
            )


# can add prot as port=80, debug =True
if __name__ == '__main__':
    app.run(debug=True)
