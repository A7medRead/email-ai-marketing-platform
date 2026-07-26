import "./Contacts.css";
import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Loading from "../../components/Loading";
import EmptyState from "../../components/EmptyState";

export default function Contacts(){

const [contacts,setContacts]=useState([]);
const [search,setSearch]=useState("");
const [company,setCompany]=useState("");
const [status,setStatus]=useState("");
const [page,setPage]=useState(1);
const [hasMore,setHasMore]=useState(true);
const [pageLoading,setPageLoading]=useState(true);
const fileInput = useRef(null);
const [message,setMessage]=useState("");
const [lists,setLists]=useState([]);
const [importList,setImportList]=useState("");
const [selected,setSelected]=useState([]);


async function importContacts(e){

const file = e.target.files[0];

if(!file)
return;


const formData = new FormData();

formData.append(
"file",
file
);


if(importList){

console.log(
"Importing to contact list:",
importList
);

formData.append(
"contact_list_id",
importList
);

}


try{

const res = await api.post(
"/contacts/import",
formData,
{
headers:{
"Content-Type":"multipart/form-data"
}
}
);


setMessage(
`Imported ${res.data.imported} contacts successfully`
);


loadContacts();


}
catch(err){

console.log(err);

setMessage(
"Import failed"
);

}

}




function loadLists(){

api.get("/contact-lists/")
.then(res=>{
setLists(res.data);
})
.catch(err=>{
console.log(err);
});

}

function loadContacts(){

api.get("/contacts/",{
params:{
page,
limit:10,
...(search && {search}),
...(company && {company}),
...(status && {status})
}
})
.then(res=>{
setContacts(res.data);
setHasMore(res.data.length === 10);
})
.catch(err=>{
console.log(err);
})
.finally(()=>{
setPageLoading(false);
});

}

useEffect(()=>{
loadContacts();
loadLists();
},[page,search,company,status]);
useEffect(()=>{
setSelected([]);
},[contacts]);




function toggleSelect(id){

if(selected.includes(id)){

setSelected(
selected.filter(x=>x!==id)
);

}else{

setSelected(
[...selected,id]
);

}

}


function toggleAll(){

if(selected.length === filtered.length){

setSelected([]);

}else{

setSelected(
filtered.map(c=>c.id)
);

}

}


async function deleteSelected(){

if(selected.length===0)
return;


if(!window.confirm("Delete selected contacts?"))
return;


try{

await api.post(
"/contacts/bulk-delete",
{
ids:selected
}
);


setMessage("Contacts deleted");

loadContacts();


}
catch(err){

console.log(err);
setMessage("Delete failed");

}

}


const filtered = contacts.filter(c => {

const fields=[
c.first_name,
c.last_name,
c.email,
c.company
]
.filter(Boolean)
.map(x=>x.toLowerCase());

const value=search.trim().toLowerCase();

return fields.some(
field=>field.startsWith(value)
);

});


if(pageLoading)
return <Loading />;


return (

<div className="page">


<div className="contacts-header">

<div>
<h1>Contacts</h1>
<p className="subtitle">
Manage your customer contacts ({contacts.length})
</p>
</div>


<div style={{display:"flex",gap:"12px"}}>

<input
type="file"
accept=".csv"
ref={fileInput}
style={{display:"none"}}
onChange={importContacts}
/>


<select
value={importList}
onChange={(e)=>setImportList(e.target.value)}
>

<option value="">
Import without list
</option>

{
lists.map(list=>(
<option key={list.id} value={list.id}>
Import to: {list.name}
</option>
))
}

</select>


<Button
onClick={()=>fileInput.current.click()}
>
📥 Import CSV
</Button>


<Button
variant="secondary"
onClick={async()=>{

try{

const res = await api.get(
"/contacts/export",
{
responseType:"blob"
}
);


const url = window.URL.createObjectURL(
new Blob([res.data])
);


const link = document.createElement("a");

link.href=url;

link.download="contacts.csv";

document.body.appendChild(link);

link.click();

link.remove();

}

catch(err){

console.log(err);

}

}}
>
📤 Export CSV
</Button>


<Link to="/contacts/create">
<Button>
+ Add Contact
</Button>
</Link>

</div>

</div>


{message && <p>{message}</p>}


<div style={{display:"flex",gap:"10px",marginBottom:"15px"}}>

<Button
variant="secondary"
onClick={toggleAll}
>
{selected.length ? "Unselect All" : "Select All"}
</Button>


<Button
variant="danger"
onClick={deleteSelected}
>
🗑 Delete Selected ({selected.length})
</Button>

</div>


<input
placeholder="Search contacts..."
value={search}
onChange={(e)=>{
setPage(1);
setSearch(e.target.value);
}}
className="contact-search"
/>


<div style={{
display:"flex",
gap:"12px",
marginTop:"15px",
marginBottom:"15px"
}}>


<input
placeholder="Filter by company"
value={company}
onChange={(e)=>{
setPage(1);
setCompany(e.target.value);
}}
/>


<select
value={status}
onChange={(e)=>{
setPage(1);
setStatus(e.target.value);
}}
>

<option value="">
All Status
</option>

<option value="ACTIVE">
Active
</option>

<option value="INACTIVE">
Inactive
</option>

</select>


</div>





<div className="contact-cards">


{
filtered.length === 0
?
<EmptyState
title="No contacts found"
message="Add contacts to start managing your audience"
/>
:
filtered.map(contact=>(

<Card className="contact-card" key={contact.id}>

<input
type="checkbox"
checked={selected.includes(contact.id)}
onChange={()=>toggleSelect(contact.id)}
/>


<div className="contact-avatar">
{contact.first_name?.[0]}{contact.last_name?.[0]}
</div>


<h2 className="contact-name">
{contact.first_name} {contact.last_name}
</h2>


<p>
📧 {contact.email}
</p>


<p>
🏢 {contact.company || "No Company"}
</p>


<span className="status-active">
{contact.status}
</span>


<div className="contact-actions">


<Link to={`/contacts/${contact.id}`}>
<Button variant="secondary">
👁 View
</Button>
</Link>


<Link to={`/contacts/${contact.id}/edit`}>
<Button variant="secondary">
✎ Edit
</Button>
</Link>


</div>


</Card>

))
}


</div>


{
(contacts.length > 0) &&
<div className="contacts-pagination">

<Button
variant="secondary"
disabled={page===1}
onClick={()=>setPage(page-1)}
>
← Previous
</Button>


<span>
Page {page}
</span>


<Button
variant="secondary"
disabled={!hasMore}
onClick={()=>setPage(page+1)}
>
Next →
</Button>


</div>
}


</div>

)

}
