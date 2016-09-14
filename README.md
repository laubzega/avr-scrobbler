# avr-scrobbler
Preserve playlist history of your Yamaha AVR.

If you ever have multiple people using a single AVR to stream music (like
during a party or if you live with roommates), from time to time you will
run into "what is/was this song I liked" question. Rather than going around
asking people (which is not always possible and also leads to unnecessary
social interactions), you may now use avr-scrobbler to continuously log what
is playing on the AVR in your network. The source/artist/album/track
information is sent to stdout and scrobbled to last.fm.

For an example from my living room see http://www.last.fm/user/LivingRoomAVR
(spare me comments about my taste in music, though).

The initial version supports only Yamaha AVRs (tested on RX-A1050, but
should work on many more models), hopefully patches for other brands will be
forthcoming.

Credit's where credit's due: initial version of send_message() was lifted from https://github.com/thomas-villagers/avsend


