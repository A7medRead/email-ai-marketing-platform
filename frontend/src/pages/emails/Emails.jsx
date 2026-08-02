import "./Emails.css";

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";

export default function Emails(){

const [emails,setEmails] = useState([]);

const [page,setPage] = useState(1);

const [pages,setPages] = useState(1);

const [search,setSearch] = useState("");

const [filter,setFilter] = useState("All emails");


useEffect(()=>{

loadEmails();

},[page]);


function loadEmails(){

api.get(`/email/history?page=${page}&limit=10`)
.then(res=>{
setEmails(res.data.items || []);
setPages(res.data.pages || 1);
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

<div className="emails-page">

<div className="emails-header">

<div>
<h1>Emails</h1>

<p className="emails-count">
{emails.length} emails created
</p>

</div>


<div className="emails-toolbar">

<input
className="email-search"
placeholder="Search emails..."
value={search}
onChange={(e)=>setSearch(e.target.value)}
/>


<select
className="email-filter"
value={filter}
onChange={(e)=>setFilter(e.target.value)}
>

<option>
All emails
</option>

<option>
Newest
</option>

<option>
Oldest
</option>

</select>


<Link
className="create-email-btn"
to="/emails/create"
>
+ Create Email
</Link>


</div>

</div>


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

{emails
.filter(email => {

const text =
`${email.subject} ${email.purpose}`
.toLowerCase();

if(search && !text.includes(search.toLowerCase())){
return false;
}

return true;

})
.sort((a,b)=>{

if(filter === "Newest"){
return new Date(b.created_at) - new Date(a.created_at);
}

if(filter === "Oldest"){
return new Date(a.created_at) - new Date(b.created_at);
}

return 0;

})
.map(email=>(

<tr
key={email.id}
className="email-row"
onClick={()=>{
window.location.href = `/emails/${email.id}`;
}}
>

<td>
<Link to={`/emails/${email.id}`}>
{email.id}
</Link>
</td>

<td className="subject-cell">

<Link to={`/emails/${email.id}`}>

<strong title={email.subject}>
✉ {email.subject}
</strong>

</Link>

</td>

<td>

<span className="purpose-badge">
🏷 {email.purpose?.length > 35
    ? email.purpose.substring(0,35) + "..."
    : email.purpose}
</span>

</td>

<td>
{new Date(email.created_at).toLocaleDateString(
    "en-US",
    {
        month:"short",
        day:"numeric",
        year:"numeric"
    }
)}
<br/>
<span className="email-time">
{new Date(email.created_at).toLocaleTimeString(
    "en-US",
    {
        hour:"2-digit",
        minute:"2-digit"
    }
)}
</span>
</td>

<td
className="actions-menu"
onClick={(e)=>e.stopPropagation()}
>

<details>

<summary>
⋮
</summary>

<div className="action-dropdown">

<button onClick={()=>{
window.location.href=`/emails/${email.id}`;
}}>
👁 View
</button>


<button onClick={()=>{
window.location.href=`/emails/create?template=${email.id}`;
}}>
📋 Template
</button>


<button onClick={()=>{
window.location.href=`/emails/create?template=${email.id}`;
}}>
📄 Duplicate
</button>


<button
className="delete-action"
onClick={()=>deleteEmail(email.id)}
>
🗑 Delete
</button>

</div>

</details>

</td>

</tr>

))}

{emails.filter(email => {

const text =
`${email.subject} ${email.purpose}`
.toLowerCase();

return !search || text.includes(search.toLowerCase());

}).length === 0 && (

<tr>
<td colSpan="5">

<div className="empty-emails">

<h3>No emails found</h3>

<p>
Try changing your search or create a new email template.
</p>

</div>

</td>
</tr>

)}

</tbody>

</table>


<div className="pagination">

<button
disabled={page === 1}
onClick={()=>setPage(page-1)}
>
← Previous
</button>


<span>
Page {page} of {pages}
</span>


<button
disabled={page === pages}
onClick={()=>setPage(page+1)}
>
Next →
</button>

</div>

</div>

)

}
