# PyNaCl Layer

This is bullshit, I hate it, it makes me sad.

If changing Python versions you'll need to also update the PyNaCl layer. This involves recreating the .zip file in this folder. 

Currently the workaround is to deploy it, go to the AWS console, and roll back the auth function to 3.8, but don't do this it's naughty, I just can't be bothered fixing it right now. 