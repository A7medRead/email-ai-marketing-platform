import Button from "../../components/Button";
import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function CreateTemplate(){

const navigate = useNavigate();


const [form,setForm]=useState({
name:"",
purpose:"",
description:"",
tone:"",
language:"",
subject:"",
body:""
});



function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

try{

await api.post("/templates/",form);

navigate("/templates");

}
catch(err){

console.log("CREATE TEMPLATE ERROR:");
console.log(err.response?.data || err);

alert(
JSON.stringify(err.response?.data || err)
);

}

}



return (

<div className="page">


<Button
variant="secondary"
onClick={()=>navigate("/templates")}
>
← Back
</Button>


<h1>
Create Template
</h1>


<p className="subtitle">
Create reusable email template
</p>



<div
style={{
maxWidth:"600px",
marginTop:"30px",
background:"#16171d",
padding:"30px",
borderRadius:"16px"
}}
>


<form
onSubmit={submit}
style={{
display:"grid",
gap:"18px"
}}
>


<input
name="name"
placeholder="Template Name"
onChange={change}
/>


<input
name="purpose"
placeholder="Purpose"
onChange={change}
/>


<textarea
name="description"
placeholder="Description"
rows="5"
onChange={change}
/>


<input
name="tone"
placeholder="Tone (Professional, Friendly...)"
onChange={change}
/>


<input
name="language"
placeholder="Language"
onChange={change}
/>


<input
name="subject"
placeholder="Email Subject"
onChange={change}
/>


<textarea
name="body"
placeholder="Email Body"
rows="8"
onChange={change}
/>


<Button type="submit">
Create Template
</Button>


</form>


</div>


</div>

)

}
