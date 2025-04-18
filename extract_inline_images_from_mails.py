import sys
import os
from email import message_from_file, policy

folder = sys.argv[1]
mailname = sys.argv[2]

with open(mailname) as f:
  msg = message_from_file(f, policy=policy.default)
  for part in msg.walk():
    print(part.get_content_type())
    filename = part.get_filename()
    print(f'>> Attachment found: {filename}')
    if filename:
      os.makedirs(folder, exist_ok=True)
      destination = os.path.join(folder, filename)
      payload = part.get_payload(decode=True)
      with open(destination, 'wb') as f1:
          f1.write(payload)