export default function EditProfileModal({
    form,
    setForm,
    save,
    close,
    uploadAvatar
}){

return (

<div className="profile-modal-bg">

<div className="profile-modal">

<div className="modal-header">
<h2>✎ Edit Profile</h2>
</div>


<label>Name</label>
<input
className="edit-input"
value={form.name || ""}
onChange={e=>setForm({...form,name:e.target.value})}
/>


<label>Phone</label>
<input
className="edit-input"
value={form.phone || ""}
onChange={e=>setForm({...form,phone:e.target.value})}
/>


<label>Country</label>
<input
className="edit-input"
value={form.country || ""}
onChange={e=>setForm({...form,country:e.target.value})}
/>


<label>City</label>
<input
className="edit-input"
value={form.city || ""}
onChange={e=>setForm({...form,city:e.target.value})}
/>


<label>Language</label>
<select
className="edit-input"
value={form.preferred_language || ""}
onChange={e=>setForm({...form,preferred_language:e.target.value})}
>
<option>English</option>
<option>Arabic</option>
</select>


<label>Tone</label>
<select
className="edit-input"
value={form.preferred_tone || ""}
onChange={e=>setForm({...form,preferred_tone:e.target.value})}
>
<option>Professional</option>
<option>Friendly</option>
<option>Casual</option>
</select>


<label>Profile Image</label>

<input
type="file"
accept="image/*"
onChange={uploadAvatar}
className="edit-input"
/>


<div className="modal-actions">

<button
className="modal-btn save-btn"
onClick={save}
>
Save Changes
</button>


<button
className="modal-btn cancel-btn"
onClick={close}
>
Cancel
</button>

</div>

</div>

</div>

)

}
