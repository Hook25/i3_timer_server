# i3_timer_server
A i3 timer server and widget to send timers over the network and display them in i3bar. I made this because I needed to start timers over the network, and have them pretty printed in the i3bar.

## Setup
- Make the server start on the host machine when you need it
- Put the client in the i3bar, if running locally, there is no parameter to set
- (Optional:) Create the aliasses to make this more confortable to use

## Configuring the server
The server has the following parameters:
- `-ip` to set the ip that can connect, put `0.0.0.0` for any, `127.0.0.1` for only local
- `-port` to set the port
- `-command` to specify the command that should be run at the end of the timer, use `{}` formatting to get the message
- `-h` prints help

## Configuring the client
The client has the following parameters:
- `-ip` to specify where is the server, use `127.0.0.1` for local
- `-port` to set the port
- `-action` to specify what the call should do, by default it provides a list of all the timers in short form
- `-h` prints help

### Possible actions
- `post_new` creates a new timer, expects 2 arguments `timespec` and `message` Example: `-action post_new 10:32:12 "Time is up"` -> Create a timer of 10h 32m 12s with the provided message
- `show_brief` default, prints a short list of all the active timers 
- `show_detail` prints a detailed list, with IDs, of all timers
- `delete` deletes a timer, expects 1 or more IDs to delete

## Bash Aliasses
I personally prefer to have the following aliasses in my `.bashrc`, to make them work you need `i3_timer_server` in your `$PATH`
```
timer() {
  local N=$1; shift

  (i3_timer_server -action post_new $N "${*:-BING}") 
}

timer_list(){
  (i3_timer_server -action show_detail)
}

timer_del(){
  (i3_timer_server -action delete $1)
}
```
## Preview
No timer

![image](https://user-images.githubusercontent.com/4686986/138283190-aeb82b38-7251-426f-887b-265928395e96.png)

Some timers

![image](https://user-images.githubusercontent.com/4686986/138283407-ac70b388-27b7-454d-8d01-50715bece6ef.png)

## Security implications
There is no authentication nor any security check on the provided command / message, therefore this process should **NOT** be exposed to any non-local and secure network (home network for example). In the future there will be both a key system for the API and a message sanity check.
