### Raspberry Pi Music Visualizer

## Collaborators

This was a class project that I worked on with one other student, unfortunately due to UVM transfering to a different student assignment repository I have since lost my partners contact information and cannot credit them directly with the work they contributed to this project.
They primarily worked on the front-end, creating a web app controller for our "smart-speaker". I primarily worked on the backend to create the code that would run the FFT (Fast Fourrier Transformation) and transform that into the various visualizations to be displayed on
an LED matrix attached to a Raspberry Pi.

## Project Description

Ultimately, the goal of the project is to have a web-app run speaker with the ability to upload music and have the speaker be able to run visualizations. This implementation runs several visualizations, one in particular showing the decibal values of various frequencies heard in a
music sample and displaying their relative heights. Another visualization took the Bass tones and interpreted them as a type of background luminocity and the other frequencies as a sun-like object.

This was ultimately successful though a very early project of mine. I think if I were to attempt doing it again I'd work harder on looking through the controller for the RGB matrix as I was using some code mostly a blackbox.
