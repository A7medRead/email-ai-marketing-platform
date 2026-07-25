import {useEffect,useState} from "react";
import {useParams,useNavigate} from "react-router-dom";
import api from "../../api/client";


export default function EditTemplate(){

const {id}=useParams();
const navigate=useNavigate();


const [form,setForm]=useState({
name:"",
purpose:"",
description:"",
tone:"",
language:""
});


useEffect(()=>{

api.get("/templates/")
.then(res=>{

const template=res.data.find(
t=>String(t.id)===String(id)
);

if(template){
setForm({
name:template.name,
purpose:template.purpose,
description:template.description,
tone:template.tone,
language:template.language
});
}

});

},[id]);



function change(e){

setForm({
...form,
[e.target.name]:e.target.value
});

}



async function submit(e){

e.preventDefault();

try{

await api.put(
`/templates/${id}`,
form
);

navigate("/templates");

}
catch(err){

console.log(err.response?.data || err);

}

}



return (

<div className="page">


<button onClick={()=>navigate("/templates")}>
← Back
</button>


<h1>
Edit Template
</h1>



<form
onSubmit={submit}
style={{
display:"grid",
gap:"18px",
maxWidth:"600px",
marginTop:"30px"
}}
>


<input
name="name"
value={form.name}
placeholder="Template Name"
onChange={change}
/>


<input
name="purpose"
value={form.purpose}
placeholder="Purpose"
onChange={change}
/>


<textarea
name="description"
value={form.description}
placeholder="Description"
rows="5"
onChange={change}
/>


<input
name="tone"
value={form.tone}
placeholder="Tone"
onChange={change}
/>


<input
name="language"
value={form.language}
placeholder="Language"
onChange={change}
/>


<button>
Save Changes
</button>


</form>


</div>

)

}
