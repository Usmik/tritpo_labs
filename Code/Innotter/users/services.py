from datetime import datetime

from Innotter.aws import s3_client
from Innotter.settings import AWS


def upload_image_to_s3(request):
    s3_path = f'{request.FILES["file"].name}_{datetime.now().strftime("%m.%d.%Y_%H:%M:%S")}'
    s3_client.put_object(Body=request.FILES['file'], Key=s3_path, Bucket=AWS['AWS_BUCKET_NAME'])
    user = request.user
    user.image_s3_path = s3_path
    user.save()
    url = s3_client.generate_presigned_url('get_object',
                                           Params={'Bucket': AWS['AWS_BUCKET_NAME'],
                                                   'Key': s3_path},
                                           ExpiresIn=3600)
    return url
