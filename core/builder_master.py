import os
import time
import re
import traceback
import json
from agents.builder_agent import BuilderAgent


class BuilderMaster:

    def __init__(self):

        self.builder = BuilderAgent()

        # =====================================================
        # PROJECT DIRECTORY
        # =====================================================
        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.projects_dir = os.path.abspath(
            os.path.join(
                self.base_dir,
                "..",
                "projects"
            )
        )

        # Create projects directory safely
        try:
            os.makedirs(
                self.projects_dir,
                exist_ok=True
            )

        except Exception as e:
            print(f"[ERROR] Failed to create projects directory: {e}")
            raise

    # =========================================================
    # SANITIZE FOLDER NAME
    # =========================================================
    def sanitize_folder_name(self, name: str) -> str:

        if not name:
            return f"project_{int(time.time())}"

        # Convert to string
        clean = str(name)

        # Remove invalid Windows characters
        clean = re.sub(
            r'[<>:"/\\|?*]',
            '',
            clean
        )

        # Replace spaces and special chars
        clean = re.sub(
            r'[\s\W]+',
            '_',
            clean
        )

        # Remove duplicate underscores
        clean = re.sub(
            r'_+',
            '_',
            clean
        )

        # Strip underscores
        clean = clean.strip('_')

        # Lowercase
        clean = clean.lower()

        # Reserved Windows names
        reserved = {
            "con", "prn", "aux", "nul",
            "com1", "com2", "com3",
            "com4", "com5", "com6",
            "com7", "com8", "com9",
            "lpt1", "lpt2", "lpt3",
            "lpt4", "lpt5", "lpt6",
            "lpt7", "lpt8", "lpt9"
        }

        if clean in reserved:
            clean = f"project_{clean}"

        # Fallback
        if not clean:
            clean = f"project_{int(time.time())}"

        # Limit length
        clean = clean[:100]

        return clean

    # =========================================================
    # UNIQUE PROJECT PATH
    # =========================================================
    def generate_unique_path(self, folder_slug):

        proj_path = os.path.join(
            self.projects_dir,
            folder_slug
        )

        # Avoid overwrite
        if not os.path.exists(proj_path):
            return proj_path

        counter = 1

        while True:

            new_path = os.path.join(
                self.projects_dir,
                f"{folder_slug}_{counter}"
            )

            if not os.path.exists(new_path):
                return new_path

            counter += 1

    # =========================================================
    # SAFE FILE WRITER
    # =========================================================
    def write_file(self, path, content):

        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(str(content))

            return True

        except Exception as e:
            print(f"[ERROR] File Write Error: {e}")
            return False

    # =========================================================
    # MAIN PROJECT BUILDER
    # =========================================================
    def launch_project(self, lead_name, pitch):

        print("\n" + "=" * 60)
        print(">> AI SWARM PROJECT BUILDER")
        print("=" * 60)

        # =====================================================
        # STEP 1: SAFE FOLDER NAME
        # =====================================================
        folder_slug = self.sanitize_folder_name(
            lead_name
        )

        proj_path = self.generate_unique_path(
            folder_slug
        )

        print(f"[BUILD] Lead Name : {lead_name}")
        print(f"[BUILD] Folder    : {os.path.basename(proj_path)}")

        # =====================================================
        # STEP 2: CREATE PROJECT DIRECTORY
        # =====================================================
        try:

            os.makedirs(
                proj_path,
                exist_ok=True
            )

        except Exception as e:
            print(f"[ERROR] Directory Creation Failed: {e}")

            # Emergency fallback
            fallback = f"build_{int(time.time())}"

            proj_path = os.path.join(
                self.projects_dir,
                fallback
            )

            os.makedirs(
                proj_path,
                exist_ok=True
            )

            print(f"[WARNING] Using fallback directory: {fallback}")

        # =====================================================
        # STEP 3: GENERATE ROADMAP
        # =====================================================
        try:

            print("[BUILD] Generating roadmap...")

            roadmap = self.builder.create_implementation_plan(
                lead_name,
                pitch
            )

            roadmap_path = os.path.join(
                proj_path,
                "roadmap.md"
            )

            self.write_file(
                roadmap_path,
                roadmap
            )

            print("[SUCCESS] Roadmap Generated")

        except Exception as e:
            print(f"[ERROR] Roadmap Generation Failed: {e}")

            self.write_file(
                os.path.join(proj_path, "roadmap_error.txt"),
                traceback.format_exc()
            )

        # =====================================================
        # STEP 4: GENERATE PROTOTYPE
        # =====================================================
        try:

            print("[BUILD] Generating prototype...")

            prototype = self.builder.generate_code_prototype(
                pitch
            )

            prototype_path = os.path.join(
                proj_path,
                "prototype.py"
            )

            self.write_file(
                prototype_path,
                prototype
            )

            print("[SUCCESS] Prototype Generated")

        except Exception as e:
            print(f"[ERROR] Prototype Generation Failed: {e}")

            self.write_file(
                os.path.join(proj_path, "prototype_error.txt"),
                traceback.format_exc()
            )

        # =====================================================
        # STEP 5: GENERATE FULL SOURCE CODE
        # =====================================================
        try:
            print("[BUILD] Generating full source code factory...")
            
            codebase_json = self.builder.generate_full_codebase(pitch)
            codebase = json.loads(codebase_json)
            
            source_dir = os.path.join(proj_path, "source_code")
            os.makedirs(source_dir, exist_ok=True)
            
            for filename, content in codebase.items():
                file_path = os.path.join(source_dir, filename)
                # Create subdirs if needed (e.g., 'app/main.py')
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                self.write_file(file_path, content)
                print(f"   - Created: {filename}")
                
            print("[SUCCESS] Full Codebase Factory Completed")

        except Exception as e:
            print(f"[ERROR] Source Code Generation Failed: {e}")
            self.write_file(
                os.path.join(proj_path, "source_error.txt"),
                traceback.format_exc()
            )

        # =====================================================
        # STEP 6: BUILD INFO
        # =====================================================
        build_info = f"""
AI SWARM BUILD REPORT
=====================

Lead Name:
{lead_name}

Generated Folder:
{os.path.basename(proj_path)}

Build Time:
{time.strftime('%Y-%m-%d %H:%M:%S')}

Project Path:
{proj_path}

Status:
SUCCESS
"""

        self.write_file(
            os.path.join(
                proj_path,
                "build_info.txt"
            ),
            build_info
        )

        print("=" * 60)
        print("[SUCCESS] BUILD COMPLETED SUCCESSFULLY")
        print(f"[INFO] Location: {proj_path}")
        print("=" * 60)

        return proj_path

    # =========================================================
    # PROPOSAL GENERATOR
    # =========================================================
    def generate_proposal(self, client_name, project_title, price, currency, milestones):
        """
        Generates a professional Markdown-based service agreement.
        """
        current_date = time.strftime('%B %d, %Y')
        
        proposal_content = f"""# 📑 SERVICE AGREEMENT & PROJECT PROPOSAL

**Date:** {current_date}  
**Client:** {client_name}  
**Service Provider:** AI Agency Swarm (Lead Generation & Automation)

---

## 1. Project Overview
This proposal outlines the strategic implementation of **{project_title}**. Our goal is to leverage autonomous AI agents to optimize your business workflows, increase efficiency, and scale outreach operations.

## 2. Scope of Work
- **AI Infrastructure:** Deployment of custom LLM-based agent swarms.
- **Data Integration:** Connecting AI agents with your existing business data.
- **Workflow Automation:** Automating repetitive tasks (Lead Gen, Outreach, Research).
- **Quality Assurance:** 7-day monitoring period after deployment.

## 3. Investment & Payment Schedule
The total investment for this project is **{currency} {price}**.

### 💎 Payment Milestones:
{milestones}

## 4. Terms & Conditions
- **Trust & Transparency:** We provide 24/7 visibility into the AI's logs.
- **Intellectual Property:** Full ownership of the custom codebase is transferred to the client upon final payment.
- **Confidentiality:** All client data is processed securely and never shared with third parties.

## 5. Acceptance
Payment of the initial deposit constitutes acceptance of this proposal and the commencement of the project.

---
*This document is generated by the AI Agency Swarm Master. For any queries, please reach out to your dedicated account manager.*
"""
        return proposal_content