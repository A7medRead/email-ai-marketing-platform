import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

export default function RichTextEditor({ value, onChange }) {

  const editor = useEditor({
    extensions: [
      StarterKit,
    ],

    content: value || "",

    immediatelyRender:false,

    onUpdate({ editor }) {
      onChange(editor.getHTML());
    },
  });


  if (!editor) return null;


  return (
    <div className="rich-editor">


      <div className="rich-toolbar">


        <button
          onClick={() =>
            editor.chain().focus().toggleBold().run()
          }
        >
          Bold
        </button>


        <button
          onClick={() =>
            editor.chain().focus().toggleItalic().run()
          }
        >
          Italic
        </button>


        <button
          onClick={() =>
            editor.chain().focus().toggleHeading({
              level:2
            }).run()
          }
        >
          H2
        </button>


        <button
          onClick={() =>
            editor.chain().focus().toggleBulletList().run()
          }
        >
          List
        </button>


        <button
          onClick={() =>
            editor.chain().focus().undo().run()
          }
        >
          Undo
        </button>


        <button
          onClick={() =>
            editor.chain().focus().redo().run()
          }
        >
          Redo
        </button>


      </div>


      <EditorContent editor={editor}/>


    </div>
  );
}
