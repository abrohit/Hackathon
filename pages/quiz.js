

function myFunction(){

    var question = document.getElementsByClassName("input-box");

    var status =  true
     for(var x=0; x<question.length; x++){
        if(question[x].value.length == 0){
        status = false
        alert('One of the Boxes is Empty')
        break;
        }
     }


    if(status){
        
    }
    
}