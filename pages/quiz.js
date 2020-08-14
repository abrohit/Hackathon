

function myFunction(){

    var question = document.getElementsByClassName("input-box");
    var typeOfQuestion = document.querySelector("select").value;

    var status =  true
     for(var x=0; x<question.length; x++){
        console.log(question[x].value +" "+ x)
        if(question[x].value.length == 0){
        status = false
        alert('One of the Boxes is Empty')
        break;
        }
     }

    //not sure how to acess user id and username
  console.log(status)
    if(status){
  const Url='http://classroomplus.herokuapp.com/question/'+question[3].value+question[0].value+ '/' + question[2].value;
  console.log(Url)
        const data={
            session_id: ""+question[0].value,
            question: ""+question[4].value,
            q_type: ""+typeOfQuestion,
            correct: ""+question[5].value,
            wrong: ""+question[6].value
        }
        
      try{
       $.post(Url, data, function(data, status){
          console.log('${data} and status is ${status}')
       });
      }catch{
        alert('Question already exists in this lecture with that number')
      }


    }
    
}

function end(){
  //take me back to homepage
}
