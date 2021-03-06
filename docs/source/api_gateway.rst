API Gateway Integration
=======================

Define an HTTP endpoint
-----------------------

SCAR allows to transparently integrate an HTTP endpoint with a Lambda function via API Gateway. To enable this functionality you only need to define an API name and SCAR will take care of the integration process (before using this feature make sure you have to correct rights set in your aws account).

The following configuration file creates a generic api endpoint that redirects the http petitions to your lambda function::

  cat >> api-cow.yaml << EOF
  functions:
    aws:
    - lambda:
        name: scar-api-cow
        container:
          image: grycap/cowsay
      api_gateway:
        name: api-cow
  EOF

  scar init -f api-cow.yaml

After the function is created you can check the API URL with the command::

  scar ls

That shows the basic function properties::

  NAME                MEMORY    TIME  IMAGE_ID            API_URL                                                             SUPERVISOR_VERSION
  ----------------  --------  ------  ------------------  ------------------------------------------------------------------  --------------------
  scar-api-cow           512     300  grycap/cowsay       https://r20bwcmdf9.execute-api.us-east-1.amazonaws.com/scar/launch  1.2.0  


CURL Invocation
---------------
You can directly invoke the API Gateway endpoint with ``curl`` to obtain the output generated by the application::

  curl -s https://r20bwcmdf9.execute-api.us-east-1.amazonaws.com/scar/launch | base64 --decode

   ________________________________________
  / Hildebrant's Principle:                \
  |                                        |
  | If you don't know where you are going, |
  \ any road will get you there.           /
   ----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

This way, you can easily provide an HTTP-based endpoint to trigger the execution of an application.

GET Request
-----------

SCAR also allows you to make an HTTP request, for that you can use the command ``invoke`` like this::

  scar invoke -f api-cow.yaml

  Request Id: e8cba9ee-5a60-4ff2-9e52-475e5fceb165
  Log Group Name: /aws/lambda/scar-api-cow
  Log Stream Name: 2019/12/20/[$LATEST]8aa8bdecba0647edae61e2e45e99ff90
   _______________________________________
  / What if everything is an illusion and \
  | nothing exists? In that case, I       |
  | definitely overpaid for my carpet.    |
  |                                       |
  \ -- Woody Allen, "Without Feathers"    /
   ---------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

This command automatically creates a `GET` request and passes the petition to the API endpoint defined previously.
Bear in mind that the timeout for the API Gateway requests is 29s. Therefore, if the function takes more time to respond, the API will return an error message.
To launch asynchronous functions you only need to add the ``-a`` parameter to the call::

  scar invoke -f api-cow.yaml -a

  Function 'scar-api-cow' launched successfully.

When you invoke an asynchronous function through the API Gateway there is no way to know if the function finishes successfully until you check the function invocation logs.

POST Request
------------

You can also pass files through the HTTP endpoint.
For the next example we will pass an image to an image transformation system.
The following files were user to define the service::

  cat >> grayify-image.sh << EOF
  #! /bin/sh
  FILE_NAME=`basename $INPUT_FILE_PATH`
  OUTPUT_FILE=$TMP_OUTPUT_DIR/$FILE_NAME
  convert $INPUT_FILE_PATH -type Grayscale $OUTPUT_FILE
  EOF

  cat >> image-parser.yaml << EOF
  functions:
    aws:
    - lambda:
        name: scar-imagemagick
        init_script: grayify-image.sh
        container:
          image: grycap/imagemagick
        output:
        - storage_provider: s3
          path: scar-imagemagick/output
      api_gateway:
        name: image-api
  EOF

  scar init -f image-parser.yaml

We are going to convert this `image <https://raw.githubusercontent.com/grycap/scar/master/examples/imagemagick/homer.png>`_.

.. image:: images/homer.png
   :align: center 

To launch the service through the api endpoint you can use the following command::

  scar invoke -f image-parser.yaml -db homer.png

The file specified after the parameter ``-db`` is codified and passed as the POST body.
The output generated will be stored in the output bucket specified in the configuration file.
Take into account that the file limitations for request response and asynchronous requests are 6MB and 128KB respectively, as specified in the `AWS Lambda documentation <https://docs.aws.amazon.com/lambda/latest/dg/limits.html>`_.

The last option available is to store the output wihtout bucket intervention.
What we are going to do is pass the generated files to the output of the function and then store them in our machine.
For that we need to slightly modify the script and the configuration file::

  cat >> grayify-image.sh << EOF
  #! /bin/sh
  FILE_NAME=`basename $INPUT_FILE_PATH`
  OUTPUT_FILE=$TMP_OUTPUT_DIR/$FILE_NAME
  convert $INPUT_FILE_PATH -type Grayscale $OUTPUT_FILE
  cat $OUTPUT_FILE
  EOF

  cat >> image-parser.yaml << EOF
  functions:
    aws:
    - lambda:
        name: scar-imagemagick
        init_script: grayify-image.sh
        container:
          image: grycap/imagemagick
      api_gateway:
        name: image-api
  EOF

  scar init -f image-parser.yaml

This can be achieved with the command::

  scar invoke -f image-parser.yaml -db homer.png -o grey_homer.png

.. image:: images/result.png
   :align: center