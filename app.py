if not df_hien_thi.empty and "generation" in df_hien_thi.columns:
        # Hàm trích xuất số thứ tự đời để sắp xếp chuẩn toán học (1, 2, ..., 8, 9, ..., 15)
        def get_gen_number(val):
            match = re.search(r'\d+', str(val))
            return int(match.group()) if match else 99
            
        df_hien_thi["_gen_sort_val"] = df_hien_thi["generation"].apply(get_gen_number)
        df_hien_thi = df_hien_thi.sort_values(by=["_gen_sort_val"], kind="stable")
        
        # Lấy danh sách các đời duy nhất và sắp xếp theo số thứ tự tăng dần
        unique_gens = df_hien_thi[["generation", "_gen_sort_val"]].drop_duplicates().sort_values("_gen_sort_val")
        
        for _, gen_row in unique_gens.iterrows():
            gen_name = gen_row["generation"]
            group = df_hien_thi[df_hien_thi["generation"] == gen_name]
            
            tree_html += f"""
            <div class="generation-row">
                <div class="generation-title">📜 {gen_name}</div>
                <div class="nodes-grid">
            """
            for idx, row in group.iterrows():
                name = str(row.get("fullName", "Chưa rõ")).strip()
                chi = str(row.get("chi", ""))
                father = str(row.get("father", "")).strip()
                
                chi_str = f" - Chi {chi}" if chi else ""
                father_str = f"<div class='node-father'>Phụ thân: {father}</div>" if father else ""

                tree_html += f"""
                    <div class="node">
                        <div class="node-name">{name}</div>
                        <div class="node-gen">{gen_name}{chi_str}</div>
                        {father_str}
                    </div>
                """
            tree_html += """
                </div>
            </div>
            """
    else:
        tree_html += "<p style='text-align: center; font-style: italic;'>Không có dữ liệu thành viên trong nhánh này.</p>"
