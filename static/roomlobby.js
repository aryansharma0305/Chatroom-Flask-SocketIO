let socket=io();
let playerslist=document.getElementById('messagelist');
let input_message=document.getElementById('input_message')
let messages_div=document.getElementById('messages_div')


async function sendmessage(){
    msg=input_message.value;
    if (msg.trim() ===''){
        console.log('msg is empy')
    }
    else{
        socket.emit('message',msg)

    }
    input_message.value=''
}



socket.on('reflectmessage',function(msgobj){
    let name=msgobj['name']
    let msg=msgobj['msg']
    let item=document.createElement('li')
    playerslist.appendChild(item)
    item.innerHTML=`<strong> ${name} : </strong> ${msg} `
    
    messages_div.scrollTop=messages_div.scrollHeight

})

socket.on('reflectconnect',function(name){
    console.log('reflect connect')
    let item=document.createElement('li')
    
    item.innerHTML=`<strong> ${name} has joined the Room !! </strong> `
    playerslist.appendChild(item)
    
    messages_div.scrollTop=messages_div.scrollHeight
})
socket.on('reflectdisconnect',function(name){
    console.log('reflect disconnect')
    let item=document.createElement('li')
    
    item.innerHTML=`<strong> ${name} has left the Room !! </strong> `
    playerslist.appendChild(item)
    messages_div.scrollTop=messages_div.scrollHeight
})



socket.emit('requestplayers');
socket.on('player_info',function(data){
    console.log(data)
    
})
