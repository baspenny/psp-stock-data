PROJECT_ID=stock-intelligence-001
CLOUD_RUN_SERVICE_NAME:=psp-stock-data

set_project:
	gcloud config set project ${PROJECT_ID}

build_image: set_project
	gcloud builds submit --tag europe-docker.pkg.dev/${PROJECT_ID}/docker/${CLOUD_RUN_SERVICE_NAME}:latest . \
		--project=${PROJECT_ID}

deploy_job: set_project
	gcloud run jobs deploy ${CLOUD_RUN_SERVICE_NAME} \
		--image=europe-docker.pkg.dev/${PROJECT_ID}/docker/${CLOUD_RUN_SERVICE_NAME}:latest \
        --region=europe-west1 \
        --project=${PROJECT_ID} \
	  	--max-retries 1

