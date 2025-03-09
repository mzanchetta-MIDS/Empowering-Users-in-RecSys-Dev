# Load book embeddings

# Imports



def load_book_embeddings(self, path, books_df):

    # We want to load in books' embeddings to make sure our model has them on hand to give direct recommendations
    # Load in via boto3 and sagemaker

    role = sagemaker.get_execution_role()
    sm_session = sagemaker.Session()
    bucket_name = sm_session.default_bucket()
    s3 = boto3.client('s3')

    # Download the file from S3 into memory
    response = s3.get_object(Bucket=bucket_name, Key=path)

    # Read the data into a BytesIO buffer
    buffer = io.BytesIO(response['Body'].read())

    # Load numpy array from buffer
    books_df['embeddings'] = [embed for embed in np.load(buffer)]

    full_book_embeddings = books_df
    
    print(full_book_embeddings)