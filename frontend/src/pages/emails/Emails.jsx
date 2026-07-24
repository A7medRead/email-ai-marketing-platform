
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";

export default function Emails(){

const [emails,setEmails] = useState([]);


useEffect(()=>{

loadEmails();

},[]);


function loadEmails(){

api.get("/email/history")
.then(res=>{
setEmails(res.data.items || []);
})
.catch(err=>{
console.log(err);
});

}


function deleteEmail(id){

api.delete(`/email/${id}`)
.then(()=>{
loadEmails();
})
.catch(err=>{
console.log(err);
});

}


return (

<div>

<h1>Emails</h1>

<p>
<Link to="/emails/create">
+ Create Email
</Link>
</p>


<table width="100%">

<thead>
<tr>
<th>ID</th>
<th>Subject</th>
<th>Purpose</th>
<th>Created</th>
<th>Actions</th>
</tr>
</thead>


<tbody>

{emails.map(email=>(

<tr key={email.id}>

<td>
<Link to={`/emails/${email.id}`}>
{email.id}
</Link>
</td>

<td>
{email.subject}
</td>

<td>
{email.purpose}
</td>

<td>
{email.created_at}
</td>

<td>
<button onClick={()=>deleteEmail(email.id)}>
Delete
</button>
</td>

</tr>

))}

</tbody>

</table>


</div>

)

}
