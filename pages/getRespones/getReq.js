function getResponses(){
    var question = document.querySelector("input").value;
    
    if(question.length == 0){
      alert('Box is Empty!')
    }else{
 
 
      const Url = 'http://classroomplus.herokuapp.com/frq/'+question;
      console.log(Url)
      $.get(Url,function(data, status){
        console.log(data)
        if(data.length != 0)
        console.log('${data}')
        else
        alert('There are no questions in that session')
      });
    }
 }
