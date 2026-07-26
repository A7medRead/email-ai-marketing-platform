import { forwardRef, useImperativeHandle } from "react";
import { useEditor, EditorContent } from "@tiptap/react";

import StarterKit from "@tiptap/starter-kit";

const RichTextEditor = forwardRef(
(
 {
   content = "",
   onChange
 },
 ref
) => {

const editor = useEditor({

  extensions:[
    StarterKit
  ],

  content,

  onUpdate({editor}){

    onChange(
      editor.getHTML()
    );

  }

});


useImperativeHandle(
 ref,
 () => ({
   commands:{
     setContent(html){

       editor?.commands.setContent(html);

     }
   }
 })
);


if(!editor){
 return null;
}


return (

<div className="rich-editor">

<div className="editor-toolbar">

<button
onClick={()=>
 editor.chain().focus().toggleBold().run()
}
>
Bold
</button>


<button
onClick={()=>
 editor.chain().focus().toggleItalic().run()
}
>
Italic
</button>


<button
onClick={()=>
 editor.chain().focus().toggleHeading({
   level:2
 }).run()
}
>
H2
</button>


<button
onClick={()=>
 editor.chain().focus().toggleBulletList().run()
}
>
List
</button>


<button
onClick={()=>
 editor.chain().focus().undo().run()
}
>
Undo
</button>


<button
onClick={()=>
 editor.chain().focus().redo().run()
}
>
Redo
</button>


</div>


<EditorContent
 editor={editor}
/>


</div>

);

});


export default RichTextEditor;
