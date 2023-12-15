

## GitHub - jaimejim/aiocoap-pubsub-broker

The [aiocoap-pubsub-broker](https://github.com/jaimejim/aiocoap-pubsub-broker) is an implementation of the IETF's draft for the publish-subscribe architecture over the Constrained Application Protocol (CoAP), specifically draft-ietf-core-coap-pubsub. This broker is developed in Python and utilizes the aiocoap library to handle CoAP communications.

For those interested in setting up a CoAP pub-sub broker, the repository provides guidelines for requirements, installation, and usage, along with demonstrations of different operations that can be performed using provided script files such as `broker.py`, `client.py`, and others.

Key features and capabilities include creating topics as "admin," discovering resources either through `.well-known/core` or by querying the collection resource `ps`, and retrieving, updating, or deleting topic configurations and data. Additionally, it supports operations like publish, subscribe (with CoAP Observe), initializing topics into a fully created state by a publisher, and filtering collections through a FETCH request on the topic collection URI.

The main requirements to use this broker are Python 3.7 or higher and the aiocoap library, which can be installed through a specified pip command to obtain the latest development version supporting iPATCH operation.

The broker is licensed under the MIT license, ensuring it is open-source and freely available for modification and distribution. It is important to note that, as per the disclaimer in the repository, some parts of the broker were quickly developed during IETF hackathons and may contain hardcoded elements, implying that it might require further customization for various use cases.

For detailed instructions on installing and running the broker, creating topics, publishing, and subscribing, one can refer to the `README.md` available in the repository which outlines each step and provides example commands to execute using the client script.


- https://github.com/jaimejim/aiocoap-pubsub-broker
