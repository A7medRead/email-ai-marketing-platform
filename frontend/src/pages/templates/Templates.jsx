import { useEffect, useState } from "react";
import api from "../../api/client";

export default function Templates(){

const [templates,setTemplates] = useState([]);

useEffect(()=>{

api.get("/templates/")
.then(res=>{
setTemplates(res.data);
})
.catch(err=>{
console.log(err);
});

},[]);


return (

<div>

<h1>Templates</h1>

<table width="100%">

<thead>
<tr>
<th>Name</th>
<th>Subject</th>
<th>Created</th>
</tr>
</thead>

<tbody>

{templates.map(t=>(

<tr key={t.id}>

<td>{t.name}</td>
<td>{t.subject}</td>
<td>{t.created_at}</td>

</tr>

))}

</tbody>

</table>

</div>

)

}
