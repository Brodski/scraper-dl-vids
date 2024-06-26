import boto3


def sendEmail(subject, body):
    ses = boto3.client('ses', region_name='us-east-1')

    # Send the email
    response = ses.send_email(
        Source='noreply@dev-captions.bski.one', # TODO update "dev"-catpions
        Destination={
            'ToAddresses': [
                'loganwallace.smash@gmail.com',
            ],
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    print(response)
