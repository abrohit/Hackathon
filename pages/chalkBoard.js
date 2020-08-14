function saveFile(){
    var file = document.getElementById("id1").value;
    console.log(file)
          // Convert the text to BLOB.
        const textToBLOB = new Blob([file], { type: 'text/plain' });
        const date = new Date();
        const dateTimeFormat = new Intl.DateTimeFormat('en', { year: 'numeric', month: 'short', day: '2-digit' })
        const [{ value: month },,{ value: day },,{ value: year }] = dateTimeFormat .formatToParts(date)

        const sFileName = `${month} ${day} ${year} Notes.txt`;	   // The file to save the data.

        let newLink = document.createElement("a");
        newLink.download = sFileName;

        if (window.webkitURL != null) {
            newLink.href = window.webkitURL.createObjectURL(textToBLOB);
        }
        else {
            newLink.href = window.URL.createObjectURL(textToBLOB);
            newLink.style.display = "none";
            document.body.appendChild(newLink);
        }

        newLink.click(); 
    }
